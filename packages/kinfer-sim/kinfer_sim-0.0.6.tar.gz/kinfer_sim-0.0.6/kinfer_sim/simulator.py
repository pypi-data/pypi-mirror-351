"""Wrapper around MuJoCo simulation."""

import logging
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NotRequired, TypedDict, TypeVar

import mujoco
import numpy as np
from kscale.web.gen.api import RobotURDFMetadataOutput
from mujoco_scenes.mjcf import load_mjmodel

from kinfer_sim.actuators import Actuator, ActuatorCommandDict, create_actuator
from kinfer_sim.viewer import get_viewer

logger = logging.getLogger(__name__)

T = TypeVar("T")

GEOM_TO_MARKER_MAPPING: dict[int, str] = {
    mujoco.mjtGeom.mjGEOM_SPHERE: "SPHERE",
    mujoco.mjtGeom.mjGEOM_BOX: "BOX",
    mujoco.mjtGeom.mjGEOM_CAPSULE: "CAPSULE",
    mujoco.mjtGeom.mjGEOM_CYLINDER: "CYLINDER",
    mujoco.mjtGeom.mjGEOM_ARROW: "ARROW",
}

MARKER_TO_GEOM_MAPPING: dict[str, int] = {v: k for k, v in GEOM_TO_MARKER_MAPPING.items()}


def _nn(value: T | None) -> T:
    if value is None:
        raise ValueError("Value is not set")
    return value


class ConfigureActuatorRequest(TypedDict):
    torque_enabled: NotRequired[bool]
    zero_position: NotRequired[float]
    kp: NotRequired[float]
    kd: NotRequired[float]
    max_torque: NotRequired[float]


@dataclass
class ActuatorState:
    position: float
    velocity: float


class ActuatorCommand(TypedDict):
    position: NotRequired[float]
    velocity: NotRequired[float]
    torque: NotRequired[float]


def get_integrator(integrator: str) -> mujoco.mjtIntegrator:
    match integrator.lower():
        case "euler":
            return mujoco.mjtIntegrator.mjINT_EULER
        case "implicit":
            return mujoco.mjtIntegrator.mjINT_IMPLICIT
        case "implicitfast":
            return mujoco.mjtIntegrator.mjINT_IMPLICITFAST
        case "rk4":
            return mujoco.mjtIntegrator.mjINT_RK4
        case _:
            raise ValueError(f"Invalid integrator: {integrator}")


def get_solver(solver: str) -> mujoco.mjtSolver:
    match solver.lower():
        case "cg":
            return mujoco.mjtSolver.mjSOL_CG
        case "newton":
            return mujoco.mjtSolver.mjSOL_NEWTON
        case _:
            raise ValueError(f"Invalid solver: {solver}")


class MujocoSimulator:
    def __init__(
        self,
        model_path: str | Path,
        model_metadata: RobotURDFMetadataOutput,
        dt: float = 0.001,
        gravity: bool = True,
        render_mode: Literal["window", "offscreen"] = "window",
        freejoint: bool = True,
        start_height: float = 1.5,
        command_delay_min: float | None = None,
        command_delay_max: float | None = None,
        drop_rate: float = 0.0,
        joint_pos_delta_noise: float = 0.0,
        joint_pos_noise: float = 0.0,
        joint_vel_noise: float = 0.0,
        joint_zero_noise: float = 0.0,
        accelerometer_noise: float = 0.0,
        gyroscope_noise: float = 0.0,
        projected_gravity_noise: float = 0.0,
        pd_update_frequency: float = 100.0,
        mujoco_scene: str = "smooth",
        integrator: str = "implicitfast",
        solver: str = "cg",
        camera: str | None = None,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> None:
        # Chooses some reasonable defaults for the simulated command latency.
        if command_delay_max is None:
            command_delay_max = dt * 0.5
        if command_delay_min is None:
            command_delay_min = command_delay_max * 0.5

        # Stores parameters.
        self._model_path = model_path
        self._metadata = model_metadata
        self._dt = dt
        self._gravity = gravity
        self._render_mode = render_mode
        self._freejoint = freejoint
        self._start_height = start_height
        self._command_delay_min = command_delay_min
        self._command_delay_max = command_delay_max
        self._drop_rate = drop_rate
        self._joint_pos_delta_noise = math.radians(joint_pos_delta_noise)
        self._joint_pos_noise = math.radians(joint_pos_noise)
        self._joint_vel_noise = math.radians(joint_vel_noise)
        self._joint_zero_noise = math.radians(joint_zero_noise)
        self._accelerometer_noise = accelerometer_noise
        self._gyroscope_noise = math.radians(gyroscope_noise)
        self._projected_gravity_noise = projected_gravity_noise
        self._update_pd_delta = 1.0 / pd_update_frequency
        self._camera = camera

        # Gets the sim decimation.
        if (control_frequency := self._metadata.control_frequency) is None:
            raise ValueError("Control frequency is not set")
        self._control_frequency = float(control_frequency)
        self._control_dt = 1.0 / self._control_frequency
        self._sim_decimation = int(self._control_dt / self._dt)

        # Gets the joint name mapping.
        if self._metadata.joint_name_to_metadata is None:
            raise ValueError("Joint name to metadata is not set")

        self._joint_name_to_id = {name: _nn(joint.id) for name, joint in self._metadata.joint_name_to_metadata.items()}
        self._joint_id_to_name = {v: k for k, v in self._joint_name_to_id.items()}
        if len(self._joint_name_to_id) != len(self._joint_id_to_name):
            raise ValueError("Joint IDs are not unique!")

        self._actuators: dict[int, Actuator] = {}
        if self._metadata.actuator_type_to_metadata is None:
            raise ValueError("Actuator metadata is missing")

        for joint_name, joint_meta in self._metadata.joint_name_to_metadata.items():
            joint_id = self._joint_name_to_id[joint_name]
            act_type = joint_meta.actuator_type or "position"
            act_meta = self._metadata.actuator_type_to_metadata.get(act_type)
            self._actuators[joint_id] = create_actuator(
                joint_meta,
                act_meta,
                dt=self._dt,
            )

        # Chooses some random deltas for the joint positions.
        self._joint_name_to_pos_delta = {
            name: random.uniform(-self._joint_pos_delta_noise, self._joint_pos_delta_noise)
            for name in self._joint_name_to_id
        }

        # Load MuJoCo model and initialize data
        logger.info("Loading model from %s", model_path)

        self._model = load_mjmodel(model_path, mujoco_scene)

        self._model.opt.timestep = self._dt
        self._model.opt.integrator = get_integrator(integrator)
        self._model.opt.solver = get_solver(solver)

        self._model.qpos0[:] = np.random.normal(0, self._joint_zero_noise) + self._model.qpos0

        self._data = mujoco.MjData(self._model)

        logger.info("Joint ID to name: %s", self._joint_id_to_name)

        if not self._gravity:
            self._model.opt.gravity[2] = 0.0

        # Initialize velocities and accelerations to zero
        if self._freejoint:
            self._data.qpos[:3] = np.array([0.0, 0.0, self._start_height])
            self._data.qpos[3:7] = np.array([0.0, 0.0, 0.0, 1.0])
            self._data.qpos[7:] = np.zeros_like(self._data.qpos[7:])
        else:
            self._data.qpos[:] = np.zeros_like(self._data.qpos)
        self._data.qvel = np.zeros_like(self._data.qvel)
        self._data.qacc = np.zeros_like(self._data.qacc)

        # Important: Step simulation once to initialize internal structures
        mujoco.mj_forward(self._model, self._data)
        mujoco.mj_step(self._model, self._data)

        self._viewer = get_viewer(
            mj_model=self._model,
            mj_data=self._data,
            render_with_glfw=True,
            render_width=frame_width,
            render_height=frame_height,
            render_shadow=False,
            render_reflection=False,
            render_contact_force=False,
            render_contact_point=False,
            render_camera_name=self._camera,
            mode=self._render_mode,
        )

        # Cache lookups after initialization
        self._sensor_name_to_id = {self._model.sensor(i).name: i for i in range(self._model.nsensor)}
        logger.debug("Sensor IDs: %s", self._sensor_name_to_id)

        self._actuator_name_to_id = {self._model.actuator(i).name: i for i in range(self._model.nu)}
        logger.debug("Actuator IDs: %s", self._actuator_name_to_id)

        # There is an important distinction between actuator IDs and joint IDs.
        # joint IDs should be at the kos layer, where the canonical IDs are assigned (see docs.kscale.dev)
        # but actuator IDs are at the mujoco layer, where the actuators actually get mapped.
        logger.debug("Joint ID to name: %s", self._joint_id_to_name)
        self._joint_id_to_actuator_id = {
            joint_id: self._actuator_name_to_id[f"{name}_ctrl"] for joint_id, name in self._joint_id_to_name.items()
        }
        self._actuator_id_to_joint_id = {
            actuator_id: joint_id for joint_id, actuator_id in self._joint_id_to_actuator_id.items()
        }

        # Add control parameters
        self._sim_time = time.time()
        self._current_commands: dict[str, ActuatorCommand] = {
            name: {"position": 0.0, "velocity": 0.0, "torque": 0.0} for name in self._joint_name_to_id
        }
        self._next_commands: dict[str, tuple[ActuatorCommand, float]] = {}

    async def step(self) -> None:
        """Execute one step of the simulation."""
        self._sim_time += self._dt

        # Process commands that are ready to be applied
        commands_to_remove = []
        for name, (target_command, application_time) in self._next_commands.items():
            if self._sim_time >= application_time:
                self._current_commands[name] = target_command
                commands_to_remove.append(name)

        # Remove processed commands
        if commands_to_remove:
            for name in commands_to_remove:
                self._next_commands.pop(name)

        mujoco.mj_forward(self._model, self._data)

        for joint_name, target_command in self._current_commands.items():
            joint = self._data.joint(joint_name)
            joint_id = self._joint_name_to_id[joint_name]
            actuator_id = self._joint_id_to_actuator_id[joint_id]

            actuator_command_dict: ActuatorCommandDict = target_command
            torque = self._actuators[joint_id].get_ctrl(
                actuator_command_dict,
                qpos=float(joint.qpos),
                qvel=float(joint.qvel),
                dt=self._dt,
            )
            logger.debug("Setting ctrl for actuator %s to %f", actuator_id, torque)
            self._data.ctrl[actuator_id] = torque

        mujoco.mj_forward(self._model, self._data)
        mujoco.mj_step(self._model, self._data)

        return self._data

    def render(self) -> None:
        self._viewer.render()

    def read_pixels(self) -> np.ndarray:
        return self._viewer.read_pixels()

    async def get_sensor_data(self, name: str) -> np.ndarray:
        """Get data from a named sensor."""
        if name not in self._sensor_name_to_id:
            raise KeyError(f"Sensor '{name}' not found")
        sensor_id = self._sensor_name_to_id[name]
        return self._data.sensor(sensor_id).data.copy()

    async def get_actuator_state(self, joint_id: int) -> ActuatorState:
        """Get current state of an actuator using real joint ID."""
        if joint_id not in self._joint_id_to_name:
            raise KeyError(f"Joint ID {joint_id} not found in config mappings")

        joint_name = self._joint_id_to_name[joint_id]
        joint_data = self._data.joint(joint_name)

        return ActuatorState(
            position=float(joint_data.qpos)
            + self._joint_name_to_pos_delta[joint_name]
            + random.uniform(-self._joint_pos_noise, self._joint_pos_noise),
            velocity=float(joint_data.qvel) + random.uniform(-self._joint_vel_noise, self._joint_vel_noise),
        )

    def command_actuators(self, commands: dict[str, ActuatorCommand]) -> None:
        """Command multiple actuators at once using real joint IDs."""
        for joint_name, command in commands.items():
            actuator_name = f"{joint_name}_ctrl"
            if actuator_name not in self._actuator_name_to_id:
                logger.warning("Joint %s not found in MuJoCo model", actuator_name)
                continue

            # Calculate random delay and application time
            delay = np.random.uniform(self._command_delay_min, self._command_delay_max)
            application_time = self._sim_time + delay

            # Randomly drop some actions.
            if random.random() < self._drop_rate:
                continue

            self._next_commands[joint_name] = (command, application_time)

    async def configure_actuator(
        self,
        joint_id: int,
        configuration: ConfigureActuatorRequest,
    ) -> None:
        """Forward configuration dict to the actuator instance."""
        if joint_id not in self._actuators:
            raise KeyError(f"Joint ID {joint_id} does not have an actuator. Known IDs: {list(self._actuators)}")

        # Keep only numeric fields (kp, kd, max_torque) and cast them to float
        cfg: dict[str, float] = {k: float(v) for k, v in configuration.items() if isinstance(v, (int, float))}

        self._actuators[joint_id].configure(**cfg)

    @property
    def sim_time(self) -> float:
        return self._sim_time

    async def reset(
        self,
        xyz: tuple[float, float, float] | None = None,
        quat: tuple[float, float, float, float] | None = None,
        joint_pos: dict[str, float] | None = None,
        joint_vel: dict[str, float] | None = None,
    ) -> None:
        """Reset simulation to specified or default state."""
        self._next_commands.clear()

        mujoco.mj_resetData(self._model, self._data)
        self._data.ctrl[:] = 0.0
        self._data.qfrc_applied[:] = 0.0
        self._data.qfrc_bias[:] = 0.0
        self._data.actuator_force[:] = 0.0

        # Resets qpos.
        qpos = np.zeros_like(self._data.qpos)
        if self._freejoint:
            qpos[:3] = np.array([0.0, 0.0, self._start_height] if xyz is None else xyz)
            qpos[3:7] = np.array([0.0, 0.0, 0.0, 1.0] if quat is None else quat)
            qpos[7:] = np.zeros_like(self._data.qpos[7:])
        else:
            qpos[:] = np.zeros_like(self._data.qpos)

        if joint_pos is not None:
            for joint_name, position in joint_pos.items():
                self._data.joint(joint_name).qpos = position

        # Resets qvel.
        qvel = np.zeros_like(self._data.qvel)
        if joint_vel is not None:
            for joint_name, velocity in joint_vel.items():
                self._data.joint(joint_name).qvel = velocity

        # Resets qacc.
        qacc = np.zeros_like(self._data.qacc)

        # Runs one step.
        self._data.qpos[:] = qpos
        self._data.qvel[:] = qvel
        self._data.qacc[:] = qacc
        mujoco.mj_forward(self._model, self._data)
        self._current_commands.clear()

    async def close(self) -> None:
        """Clean up simulation resources."""
        try:
            self._viewer.close()
        except Exception as e:
            logger.error("Error closing viewer: %s", e)

    @property
    def timestep(self) -> float:
        return self._model.opt.timestep
