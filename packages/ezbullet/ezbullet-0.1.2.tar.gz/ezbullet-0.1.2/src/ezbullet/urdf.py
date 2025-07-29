from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pybullet as p
import trimesh
from attrs import define, field
from ezpose import SE3, SO3
from numpy.typing import ArrayLike

from .data import JointInfo, JointState
from .utils import generate_frame_urdf, generate_temp_urdf
from .world import Body, World


@define(repr=False)
class URDF(Body):
    path: str
    fixed: bool
    scale: float
    dof: int
    joint_info: list[JointInfo]
    movable_joints: np.ndarray
    pos_ctrl_gain_p: list[float]
    pos_ctrl_gain_d: list[float]
    max_torque: list[float]
    T_com: SE3 = field(init=False)

    def __attrs_post_init__(self):
        self.T_com = super().get_pose()
        self.set_joint_angles(self.neutral)

    @classmethod
    def create(
        cls,
        name,
        world: World,
        path: Path | str,
        fixed: bool = True,
        scale: float = 1.0,
        ghost: bool = False,
        position_gain: float = 0.1,
        velocity_gain: float = 1.0,
    ):
        if name in world.bodies_and_ghosts:
            print("Body name already exists.")
            return world.bodies_and_ghosts[name]
            # world.remove_body(name)

        # flags = p.URDF_USE_INERTIA_FROM_FILE if mass is not None else 0
        uid = world.loadURDF(
            fileName=str(path),
            useFixedBase=fixed,
            globalScaling=scale,
            # flags=flags, # TODO
        )
        dof = world.getNumJoints(uid)

        joint_info = []
        movable_joints = []
        for i in range(dof):
            info = JointInfo(*world.getJointInfo(uid, i))
            joint_info.append(info)
            if info.movable:
                movable_joints.append(i)
        movable_joints = np.array(movable_joints)
        position_gain = [position_gain] * len(movable_joints)
        pos_ctrl_gain_d = [velocity_gain] * len(movable_joints)

        max_torque = [
            info.joint_max_force
            for info in joint_info
            if info.joint_index in movable_joints
        ]

        mass = None
        body = cls(
            world=world,
            uid=uid,
            name=name,
            mass=mass,
            ghost=ghost,
            path=path,
            fixed=fixed,
            scale=scale,
            dof=dof,
            joint_info=joint_info,
            movable_joints=movable_joints,
            pos_ctrl_gain_p=position_gain,
            pos_ctrl_gain_d=pos_ctrl_gain_d,
            max_torque=max_torque,
        )

        if ghost:
            # TODO -> setCollisionFilterGroupMask
            # TODO: Do something here if collision behavior should be changed
            world.ghosts[name] = body
            body.disable_collision()

        else:
            world.bodies[name] = body
        return body

    @classmethod
    def from_trimesh(
        cls,
        name: str,
        world: World,
        visual_mesh: trimesh.Trimesh,
        col_mesh: trimesh.Trimesh,
        fixed: bool,
        rgba=[1, 1, 1, 1],
    ):
        import tempfile

        with tempfile.TemporaryDirectory() as tempdir:
            urdf_path = generate_temp_urdf(
                visual_mesh, tempdir, rgba, col_mesh=col_mesh
            )
            obj = cls.create(name, world, urdf_path, fixed=fixed, scale=1.0)
        return obj

    @property
    def lb(self):
        return np.array(
            [joint.joint_lower_limit for joint in self.joint_info if joint.movable]
        )

    @property
    def ub(self):
        return np.array(
            [joint.joint_upper_limit for joint in self.joint_info if joint.movable]
        )

    @property
    def neutral(self):
        return (self.lb + self.ub) / 2

    @contextmanager
    def set_joint_angles_context(self, q):
        joints_temp = self.get_joint_angles()
        self.set_joint_angles(q)
        yield
        self.set_joint_angles(joints_temp)

    def set_pose(self, pose):
        """This is because, super().set_pose is setting a pose of base inertial frame.
        This differs from initial load state of the URDF."""
        super().set_pose(pose @ self.T_com)

    def get_pose(self):
        return super().get_pose() @ self.T_com.inv()

    def get_joint_states(self):
        return [
            JointState(*s)
            for s in self.world.getJointStates(self.uid, self.movable_joints)
        ]

    def get_joint_angles(self):
        return np.array([s.pos for s in self.get_joint_states()])

    def get_joint_velocities(self):
        return np.array([s.vel for s in self.get_joint_states()])

    def set_joint_angle(self, i, angle):
        self.world.resetJointState(self.uid, jointIndex=i, targetValue=angle)

    def set_joint_angles(self, angles):
        assert len(angles) == len(
            self.movable_joints
        ), f"num_angle is not matched: {len(angles)} vs {len(self.movable_joints)}"
        for i, angle in zip(self.movable_joints, angles):
            self.set_joint_angle(i, angle)

    def get_joint_frame_pose(self, joint_idx):
        assert len(self.joint_info) > joint_idx
        parent_link_idx = joint_idx - 1
        parent_link_pose = self.get_link_pose(parent_link_idx)
        pos = self.joint_info[joint_idx].parent_frame_pos
        quat = self.joint_info[joint_idx].parent_frame_orn
        rel_pose = SE3(SO3.from_quat(quat), pos)
        return parent_link_pose @ rel_pose

    def get_link_idx_by_name(self, link_name: str):
        idx = [j.joint_index for j in self.joint_info if j.link_name == link_name]
        if len(idx) == 0:
            return None
        return idx[0]

    def get_link_pose(self, link_idx: int | str, frame="com"):
        if isinstance(link_idx, str):
            link_idx = self.get_link_idx_by_name(link_idx)
        assert len(self.joint_info) > link_idx
        if link_idx == -1:
            return super().get_pose()
        if frame == "com":
            pos, xyzw = self.world.getLinkState(self.uid, link_idx)[:2]
        elif frame == "urdf":
            pos, xyzw = self.world.getLinkState(self.uid, link_idx)[4:6]
        return SE3(SO3.from_quat(xyzw), pos)

    def get_aabb(self, link_idx: int | str = "all"):
        """if link_idx == "all", it computes the overall boundingbox"""
        if link_idx == "all":
            lb, ub = np.full(3, np.inf), np.full(3, -np.inf)
            link_indices = [-1] + [i for i in range(self.dof)]
            for idx in link_indices:
                lower, upper = super().get_aabb(idx)
                lb, ub = np.minimum(lb, lower), np.maximum(ub, upper)
            return lb, ub
        else:
            return super().get_aabb(link_idx)

    def forward_kinematics(self, q: ArrayLike, link_idx: int):
        with self.set_joint_angles_context(q):
            pose = self.get_link_pose(link_idx, frame="urdf")
        return pose

    def inverse_kinematics(
        self,
        target_pose: SE3,
        link_idx: int,
        validate=True,
        max_iter=10,
        pos_tol=1e-3,
        start_with_neutral=True,
        verbose=False,
    ):
        solved = False
        if start_with_neutral:
            q = self.neutral
        else:
            q = self.get_joint_angles()
        if not isinstance(link_idx, int):
            link_idx = self.get_link_idx_by_name(link_idx)

        with self.set_joint_angles_context(q):
            for _ in range(max_iter):
                ik_sol = self.world.calculateInverseKinematics(
                    bodyIndex=self.uid,
                    endEffectorLinkIndex=link_idx,
                    targetPosition=target_pose.trans,
                    targetOrientation=target_pose.rot.as_quat(),
                )
                # update initial joint angles to ik solution
                self.set_joint_angles(ik_sol)
                if not validate:
                    solved = True
                    break

                pose_sol = self.forward_kinematics(ik_sol, link_idx)
                trans_err = np.linalg.norm(pose_sol.trans - target_pose.trans)
                is_in_bound = np.all(ik_sol >= self.lb) and np.all(ik_sol <= self.ub)
                is_near_target = trans_err < pos_tol
                if is_near_target and is_in_bound:
                    solved = True
                    break

        if not solved:
            if verbose:
                print(f"ik not solved. pos error = {trans_err}")
            return None
        else:
            if verbose:
                print(f"ik solved. pos error = {trans_err}")
            return np.array(ik_sol)  # if solved else None

    def set_ctrl_target_joint_angles(self, q, max_torque=None):
        assert len(q) == len(self.movable_joints)
        if max_torque is None:
            max_torque = self.max_torque
        elif isinstance(max_torque, float):
            max_torque = [max_torque] * len(self.movable_joints)

        self.world.setJointMotorControlArray(
            self.uid,
            jointIndices=self.movable_joints,
            controlMode=p.POSITION_CONTROL,
            targetPositions=q,
            forces=max_torque,
            positionGains=self.pos_ctrl_gain_p,
            velocityGains=self.pos_ctrl_gain_d,
        )

    def set_ctrl_target_joint_velocities(self, qdot, max_torque=None):
        assert len(qdot) == len(self.movable_joints)
        if max_torque is None:
            max_torque = self.max_torque
        elif isinstance(max_torque, float):
            max_torque = [max_torque] * len(self.movable_joints)

        self.world.setJointMotorControlArray(
            self.uid,
            jointIndices=self.movable_joints,
            controlMode=p.VELOCITY_CONTROL,
            targetVelocities=qdot,
            forces=self.max_torque,
            # positionGains=self.pos_ctrl_gain_p,
            # velocityGains=self.pos_ctrl_gain_d,
        )

    def get_jacobian(self, q, link_idx, local_position=[0, 0, 0]):
        jac_trans, jac_rot = self.world.calculateJacobian(
            bodyUniqueId=self.uid,
            linkIndex=link_idx,
            localPosition=local_position,
            objPositions=q.tolist(),
            objVelocities=np.zeros_like(q).tolist(),
            objAccelerations=np.zeros_like(q).tolist(),
        )
        return np.vstack([jac_trans, jac_rot])


class Frame(URDF):
    @classmethod
    def create(cls, name: str, world: World, length=0.05, radius=0.005):
        import tempfile

        with tempfile.TemporaryDirectory() as tempdir:
            urdf_path = generate_frame_urdf(
                tempdir, length, radius
            )  # TODO:add mass, inertial information
            # Note: "frame.urdf" has no collision shape
            frame = super().create(name, world, urdf_path, fixed=True, ghost=True)
        return frame
