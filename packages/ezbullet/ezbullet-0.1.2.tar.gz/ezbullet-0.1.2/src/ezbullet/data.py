import pybullet as p
from attrs import define, field

"""Information Structure used in Pybullet
"""
conv_str = lambda x: x.decode("ascii") if isinstance(x, bytes) else x


@define
class JointState:
    pos: float
    vel: float
    wrench: tuple[float]  # reaction force
    torque: float  # applied motor torque


@define
class JointInfo:
    joint_index: int
    joint_name: str = field(converter=conv_str)
    joint_type: int
    q_index: int
    u_index: int
    flags: int
    joint_damping: float
    joint_friction: float
    joint_lower_limit: float
    joint_upper_limit: float
    joint_max_force: float
    joint_max_velocity: float
    link_name: str = field(converter=conv_str)
    joint_axis: tuple[float]
    parent_frame_pos: tuple[float]
    parent_frame_orn: tuple[float]
    parent_index: int

    @property
    def movable(self):
        return self.joint_type != p.JOINT_FIXED


@define
class DistanceInfo:
    contact_flag: bool
    bodyA: int
    bodyB: int
    linkA: int
    linkB: int
    position_on_A: tuple[float]
    position_on_B: tuple[float]
    contact_normal_on_B: tuple[float]
    contact_distnace: float
    normal_force: float
    lateral_frictionA: float
    lateral_friction_dirA: tuple[float]
    lateral_frictionB: float
    lateral_friction_dirB: tuple[float]


@define
class ContactInfo:
    contactFlag: int  # nothing
    bodyA: int
    bodyB: int
    link_indexA: int
    link_indexB: int
    position_on_A: tuple[float]
    position_on_B: tuple[float]
    contact_normal_on_B: tuple[float]
    contact_distance: float
    normal_force: float
    lateral_friction1: float
    lateral_friction_dir1: tuple[float]
    lateral_friction2: float
    lateral_friction_dir2: tuple[float]


@define
class DynamicsInfo:
    mass: float
    lateral_friction: float
    local_inertial_diagonal: tuple[float]
    local_inertial_pos: tuple[float]
    local_inertial_orn: tuple[float]
    restitution: float
    rolling_friction: float
    spinning_friction: float
    contact_damping: float
    contact_stiffness: float
    body_type: int
    collision_margin: float


@define
class ConstraintInfo:
    parent_body: int
    parent_link: int
    child_body: int
    child_link: int
    constr_type: int
    joint_axis: tuple[float]
    parent_frame_pos: tuple[float] = None
    parent_frame_orn: tuple[float] = None
    child_frame_pos: tuple[float] = None
    child_frame_orn: tuple[float] = None

    def to_dict(self):
        res = dict(
            parentBodyUniqueId=self.parent_body,
            parentLinkIndex=self.parent_link,
            childBodyUniqueId=self.child_body,
            childLinkIndex=self.child_link,
            jointType=self.constr_type,
            jointAxis=self.joint_axis,
            parentFramePosition=self.parent_frame_pos,
            parentFrameOrientation=self.parent_frame_orn,
            childFramePosition=self.child_frame_pos,
            childFrameOrientation=self.child_frame_orn,
        )
        return {k: v for k, v in res.items() if v is not None}
