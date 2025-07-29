import pytest

import numpy as np
from ezpose import SE3, SO3
import ezbullet as eb
import trimesh
import pybullet as p


@pytest.fixture
def world():
    world = eb.World(gui=True)
    ground_mesh = trimesh.creation.box(extents=[10, 10, 0.1])
    ground = eb.URDF.from_trimesh(
        "ground", world, ground_mesh, ground_mesh, fixed=True
    )
    box = eb.Box.create("box", world, [0.05, 0.05, 0.05])
    return world


def test_transform(world: eb.World):
    box = world.bodies["box"]
    box.set_pose(SE3(rot=SO3.random(), trans=[0, 0, 0.1]))


# def test_constraint():
#     name = "box"
#     body = eb.Box.create(name, world, [0.05, 0.05, 0.05])
#     dummy_link_x = eb.Body.create_empty_body(f"{name}_dummy_link_x", world)
#     dummy_link_z = eb.Body.create_empty_body(f"{name}_dummy_link_z", world)
#     x_constr = p.createConstraint(
#         parentBodyUniqueId=-1,
#         parentLinkIndex=-1,
#         childBodyUniqueId=body.uid,
#         childLinkIndex=-1,
#         jointType=p.JOINT_PRISMATIC,
#         jointAxis=[1, 0, 0],  # x축 이동 허용
#         parentFramePosition=[0, 0, 0],
#         childFramePosition=[0, 0, 0]
#     )
#     z_constr = p.createConstraint(
#         parentBodyUniqueId=dummy_link_x.uid,
#         parentLinkIndex=-1,
#         childBodyUniqueId=dummy_link_z.uid,
#         childLinkIndex=-1,
#         jointType=p.JOINT_PRISMATIC,
#         jointAxis=[0, 0, 1],  # z축 이동 허용
#         parentFramePosition=[0, 0, 0],
#         childFramePosition=[0, 0, 0]
#     )
#     world.create_constraint(f"{name}_x_constr", x_constr)
#     world.create_constraint(f"{name}_z_constr", z_constr)
#     world.change_constraint(f"{name}_x_constr", maxForce=100)
#     world.change_constraint(f"{name}_z_constr", maxForce=100)
