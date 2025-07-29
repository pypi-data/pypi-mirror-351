from __future__ import annotations

import time
from contextlib import contextmanager

import numpy as np
import pybullet as p
from attrs import define
from ezpose import SE3, SO3
from pybullet_utils.bullet_client import BulletClient
from typing import Callable

from .data import ConstraintInfo, ContactInfo, DistanceInfo, DynamicsInfo
from .shape import ShapeBase


class World(BulletClient):
    worlds: dict[str, World] = dict()
    gui_world_exists = False

    @classmethod
    def __new__(cls, *args, **kwargs):
        """This prevents to create two visualizers"""
        gui = True
        if len(args) > 1:
            gui = args[1]
        elif "gui" in kwargs:
            gui = kwargs["gui"]

        if "gui" in cls.worlds and gui:
            print("You can't create two visualizers")
            print("Load the existing world")
            return cls.worlds["gui"]
        else:
            world = super().__new__(cls)

        if gui:
            # print('create gui world')
            cls.worlds["gui"] = world
        else:
            # print('create no gui world')
            if "no_gui" not in cls.worlds:
                cls.worlds["no_gui"] = []
            cls.worlds["no_gui"].append(world)
        return world

    def __init__(
        self,
        gui=True,
        z_gravity=-9.81,
        dt=0.005,
        solver_iter=150,
        realtime=True,
        realtime_factor=0.5,
        background_color=None,
    ):
        if hasattr(self, "_init"):
            return  # preventing multiple initialization

        self.gui = gui
        self.dt = dt
        self.solver_iter = solver_iter
        self.realtime = realtime
        self.realtime_factor = realtime_factor
        self.gravity = z_gravity

        options = ""
        if background_color is not None:
            background_color = np.array(background_color).astype(np.float64)
            options = f"--background_color_red={background_color[0]} \
                        --background_color_green={background_color[1]} \
                        --background_color_blue={background_color[2]}"

        if gui:
            if self.gui_world_exists:
                return
            else:
                self.gui_world_exists = True
        connection_mode = p.GUI if gui else p.DIRECT

        super().__init__(connection_mode=connection_mode, options=options)
        time.sleep(1.0)

        if self.gui:
            self.pause_button_uid = p.addUserDebugParameter("turn off loop", 1, 0, 1)

        self.reset()
        self.watch_workspace()
        self._init = True
        self._step_cb = None

    @contextmanager
    def no_rendering(self):
        self.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 0)
        yield
        self.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 1)

    def set_step_callback(self, callback:Callable):
        self._step_cb = callback

    def watch_workspace(
        self, target_pos=[0, 0, 0], distance=1.0, cam_yaw=45, cam_pitch=-35
    ):
        self.resetDebugVisualizerCamera(
            cameraDistance=distance,
            cameraYaw=cam_yaw,
            cameraPitch=cam_pitch,
            cameraTargetPosition=target_pos,
        )

    @property
    def bodies_and_ghosts(self):
        return {**self.bodies, **self.ghosts}

    def get_body(self, name):
        if name in self.bodies:
            return self.bodies[name]
        return None

    def set_gravity(self, force_z=-9.81):
        self.setGravity(0, 0, force_z)

    def reset(self):
        self.resetSimulation()
        self.setPhysicsEngineParameter(
            fixedTimeStep=self.dt, numSolverIterations=self.solver_iter
        )
        self.t = 0.0
        self.bodies: dict[str, Body] = dict()
        self.shapes: dict[str, ShapeBase] = dict()
        self.ghosts: dict[str, Body] = dict()
        self.debug_items: dict[str, int] = dict()  # not wrapped by class
        self.constr: dict[str, int] = dict()  # not wrapped by class
        self.set_gravity(self.gravity)

    def step(self, no_dynamics=False):
        if no_dynamics:
            self.performCollisionDetection()
        else:
            self.stepSimulation()
        if self._step_cb is not None:
            self._step_cb()
        
        # add delay for realtime visualization
        if self.gui and self.realtime:
            time.sleep(self.dt * self.realtime_factor)
        self.t += self.dt

    def show(self):
        """Start infinite loop to visualize for macos"""
        num_quit = p.readUserDebugParameter(self.pause_button_uid)

        polling_rate = 100
        while True:
            self.step(no_dynamics=True)
            time.sleep(1 / polling_rate)
            quit = p.readUserDebugParameter(self.pause_button_uid)
            if quit >= num_quit + 1:
                break

    def get_shape_id(self, shape: ShapeBase):
        if shape in self.shapes:
            return self.shapes[shape]

        viz_id = self.createVisualShape(**shape.get_viz_query())
        col_id = (
            -1 if shape.ghost else self.createCollisionShape(**shape.get_col_query())
        )

        self.shapes[shape] = (viz_id, col_id)
        return self.shapes[shape]

    def remove_body(self, body: str | Body | BodyContainer):
        if isinstance(body, str):
            body = self.bodies_and_ghosts[body]

        def _remove_body(body: str | Body | BodyContainer, body_dict: dict[str, Body]):
            if isinstance(body, BodyContainer):
                for b in body.bodies:
                    self.removeBody(b.uid)  # delete all contained bodies
            elif isinstance(body, Body):
                self.removeBody(body.uid)
            del body_dict[body.name]

        if body.ghost:
            _remove_body(body, self.ghosts)
        else:
            _remove_body(body, self.bodies)

    def remove_all_debugitems(self):
        self.removeAllUserDebugItems()

    def remove_debug_item(self, name):
        if name in self.debug_items:
            self.removeUserDebugItem(self.debug_items[name])
            del self.debug_items[name]

    def add_debug_line(self, p_from, p_to, color=[1, 0, 0], name=None):
        """if name is not None, debug uid is tracked in self.debug_items"""
        uid = self.addUserDebugLine(
            lineFromXYZ=p_from, lineToXYZ=p_to, lineColorRGB=color
        )

        if name is not None:
            if name in self.debug_items:
                self.remove_debug_item(name)
            self.debug_items[name] = uid

    def add_debug_pcd(self, points, color=[1, 0, 0], size=5, name=None):
        """if name is not None, debug uid is tracked in self.debug_items"""
        if not isinstance(color, np.ndarray):
            color = np.array(color)
        if len(color.shape) == 1:
            num_points = points.shape[0]
            color = color[None, ...].repeat(num_points, axis=0)
        uid = self.addUserDebugPoints(
            pointPositions=points, pointColorsRGB=color, pointSize=size
        )

        if name is not None:
            if name in self.debug_items:
                self.remove_debug_item(name)
            self.debug_items[name] = uid
        return uid

    def draw_bounding_box(self, length, center=np.zeros(3)):
        vertices = np.array(list(np.ndindex((2, 2, 2))))
        edges = np.array(
            [
                (0, 1),
                (0, 2),
                (0, 4),
                (1, 3),
                (1, 5),
                (2, 3),
                (2, 6),
                (3, 7),
                (4, 5),
                (4, 6),
                (5, 7),
                (6, 7),
            ]
        )
        point_from = (vertices[edges[:, 0]] - 0.5) * length + center
        point_to = (vertices[edges[:, 1]] - 0.5) * length + center

        for p1, p2 in zip(point_from, point_to):
            self.add_debug_line(p1, p2, color=[0.5, 0.5, 0.5])

    def draw_frustum(self, pose_offset: SE3 = None, w=0.1, h=0.07, d=0.05):
        if pose_offset is None:
            pose_offset = SE3()

        w2, h2 = w * 1.5, h * 1.5
        # Define vertices of the frustum (top and bottom faces)
        top_vertices = np.array(
            [
                [-w / 2, -h / 2, 0],
                [w / 2, -h / 2, 0],
                [w / 2, h / 2, 0],
                [-w / 2, h / 2, 0],
            ]
        )

        bottom_vertices = np.array(
            [
                [-w2 / 2, -h2 / 2, d],
                [w2 / 2, -h2 / 2, d],
                [w2 / 2, h2 / 2, d],
                [-w2 / 2, h2 / 2, d],
            ]
        )

        # Combine the top and bottom vertices
        vertices = np.vstack([top_vertices, bottom_vertices])

        # Define the edges connecting the vertices (top, bottom, and sides)
        edges = np.array(
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),  # top face edges
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 4),  # bottom face edges
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),  # side edges connecting top and bottom
            ]
        )

        # Offset the vertices by the center position
        # vertices += center
        vertices = pose_offset.apply(vertices)

        # Draw the edges as lines
        for edge in edges:
            p1, p2 = vertices[edge[0]], vertices[edge[1]]
            self.add_debug_line(p1, p2, color=[1, 0, 0])

    def save_state(self, return_uid=False):
        if return_uid:
            return self.saveState()
        else:
            self._state_uid = self.saveState()

    def restore_state(self, state_uid=None):
        if state_uid is None:
            state_uid = self._state_uid
        return self.restoreState(state_uid)

    def get_distance_info(
        self,
        body1: Body,
        body2: Body,
        link1: int = None,
        link2: int = None,
        tol: float = 0.0,
    ):
        kwargs = dict()
        kwargs["bodyA"] = body1.uid
        kwargs["bodyB"] = body2.uid
        if link1 is not None:
            kwargs["linkIndexA"] = link1
        if link2 is not None:
            kwargs["linkIndexB"] = link2
        kwargs["distance"] = tol
        results = self.getClosestPoints(**kwargs)
        return [DistanceInfo(*info) for info in results]

    def get_contact_info(
        self,
        body1: Body,
        body2: Body = None,
        link1: int = None,
        link2: int = None,
    ):
        """world.step(no_dynamics=True) should be called before using"""
        kwargs = dict()
        kwargs["bodyA"] = body1.uid
        if body2 is not None:
            kwargs["bodyB"] = body2.uid
        if link1 is not None:
            kwargs["linkIndexA"] = link1
        if link2 is not None:
            kwargs["linkIndexB"] = link2
        results = self.getContactPoints(**kwargs)
        return [ContactInfo(*info) for info in results]

    def wait_to_stablize(
        self, wait_time=0.1, timeout=5.0, tol=0.01, polling_period=100
    ):
        for i in range(int(wait_time / self.dt)):
            self.step()

        t = 0.0
        while t < timeout:
            for _ in range(polling_period):
                self.step()
            t += self.dt * polling_period

            chk_all_bodies_rest = all(
                [
                    np.linalg.norm(body.get_velocity()) < tol
                    for body in self.bodies.values()
                ]
            )

            if chk_all_bodies_rest:
                break
        return

    def create_constraint(self, name, constr_info: ConstraintInfo):
        if name in self.constr:
            # constraint exists already
            return
        if constr_info.child_body is None:
            constr_info.child_body = -1

        self.constr[name] = self.createConstraint(**constr_info.to_dict())

    # TODO: make it clear
    def change_constraint(self, name, **kwargs):
        self.changeConstraint(self.constr[name], **kwargs)

    def remove_constraint(self, name):
        if name in self.constr:
            self.removeConstraint(self.constr[name])
            del self.constr[name]

    def apply_external_force(
        self, body: Body, force: np.ndarray, pos: np.ndarray, link: int = -1
    ):
        """Note that this method will only work 
        when explicitly stepping the simulation using stepSimulation"""
        p.applyExternalForce(body.uid, link, force, pos, p.WORLD_FRAME)


@define(repr=False)
class Body:
    world: World
    uid: int
    name: str
    mass: float
    ghost: bool

    def set_pose(self, pose: SE3):
        self.world.resetBasePositionAndOrientation(
            self.uid, pose.trans, pose.rot.as_quat()
        )

    def get_pose(self):
        pos, orn = self.world.getBasePositionAndOrientation(self.uid)
        return SE3(SO3.from_quat(orn), pos)

    def get_velocity(self):
        linear, angular = self.world.getBaseVelocity(self.uid)
        return linear, angular

    def is_collision_with(
        self, other_body: Body, ignore_fixed_base: bool = True, tol=0.0, verbose=False
    ):
        distance_info = self.world.get_distance_info(self, other_body, tol=tol)
        if hasattr(self, "fixed") and self.fixed and ignore_fixed_base:
            # ignore base collisions of fixed bodies
            distance_info = [info for info in distance_info if info.linkA != -1]

        if verbose:
            if len(distance_info) == 0:
                print("no collision")
            else:
                print(f"Body {self.name} collision with {other_body.name}")
        return any(distance_info)

    def is_in_collision(
        self,
        exclude: tuple[Body | BodyContainer] = tuple(),
        tol=0.0,
        ignore_fixed_base=False,
        verbose=False,
    ):
        for other in self.world.bodies.values():
            if other is self or other in exclude:
                continue

            if isinstance(other, BodyContainer):
                for _other in other.bodies:
                    if self is _other:
                        continue
                    if self.is_collision_with(
                        _other,
                        tol=tol,
                        ignore_fixed_base=ignore_fixed_base,
                        verbose=verbose,
                    ):
                        return True
            else:
                if self.is_collision_with(
                    other, tol=tol, ignore_fixed_base=ignore_fixed_base, verbose=verbose
                ):
                    return True
        return False

    def disable_collision(self):
        self.world.setCollisionFilterGroupMask(self.uid, -1, 0, 0)
        if hasattr(self, "joint_info"):
            for link_idx in range(len(self.joint_info)):
                self.world.setCollisionFilterGroupMask(self.uid, link_idx, 0, 0)

    def get_dynamics_info(self, link_idx=-1):
        return DynamicsInfo(*self.world.getDynamicsInfo(self.uid, link_idx))

    def set_dynamics_info(self, link_idx=-1, **kwargs):
        """input_dict should contain key and value of the changeDynamics()
        mass, lateralFriction, restitution, rollingFriction, spinningFriction ..."""
        self.world.changeDynamics(
            bodyUniqueId=self.uid, linkIndex=link_idx, **kwargs
        )

    def get_aabb(self, link_idx=-1):
        lower, upper = self.world.getAABB(self.uid, linkIndex=link_idx)
        lower, upper = np.array(lower), np.array(upper)
        return lower, upper

    def change_color(self, rgba, link_idx=-1):
        self.world.changeVisualShape(
            objectUniqueId=self.uid, linkIndex=link_idx, rgbaColor=rgba
        )

    @classmethod
    def create_empty_body(self, name, world):
        mass = 0.
        uid = p.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=-1,
            baseVisualShapeIndex=-1,
            basePosition=[0., 0., 0.])
        return Body(
            world=world, 
            uid=uid, 
            name=name, 
            mass=mass, 
            ghost=True
        )

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.name}"
    


@define
class BodyContainer:
    """Body container"""

    name: str
    world: World
    bodies: list[Body]
    relative_poses: list[Body]
    ghost: bool

    def __attrs_post_init__(self):
        for body in self.bodies:
            del self.world.bodies[body.name]
        self.world.bodies[self.name] = self

    @classmethod
    def from_bodies(cls, name: str, bodies: list[Body]):
        """The first body will be the reference body"""
        world = bodies[0].world
        rel_poses = [body.get_pose() for body in bodies]
        ref_pose = rel_poses[0]
        rel_poses = [ref_pose.inv() @ pose for pose in rel_poses]
        ghost = all([body.ghost for body in bodies])
        return cls(name, world, bodies, rel_poses, ghost)

    def get_pose(self):
        return self.bodies[0].get_pose()

    def set_pose(self, pose: SE3):
        # self.pose = pose
        poses = [pose @ rel_pose for rel_pose in self.relative_poses]
        for pose, body in zip(poses, self.bodies):
            body.set_pose(pose)

    def get_velocity(self):
        return self.bodies[0].get_velocity()

    def is_in_collision(self, verbose=False):
        for other in self.world.bodies.values():
            if self is other:
                continue

            for body in self.bodies:
                if body.is_in_collision(verbose=verbose):
                    return True
        return False
