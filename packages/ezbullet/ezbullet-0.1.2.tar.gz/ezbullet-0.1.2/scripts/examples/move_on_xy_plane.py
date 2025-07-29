import pybullet as p
import ezbullet as eb
from ezpose import SE3, SO3
import trimesh
import numpy as np

world = eb.World(gui=True, z_gravity=0.)
ground_mesh = trimesh.creation.box(extents=[10, 10, 0.1])
ground = eb.URDF.from_trimesh("ground", world, ground_mesh, ground_mesh, fixed=True)
ground.set_pose(SE3(trans=[0,0,-0.05]))

def cb():
    tires: list[eb.Body] = [body for name, body in world.bodies.items() if "tire" in name]
    for tire in tires:
        pose = tire.get_pose()
        rotvec = pose.rot.as_rotvec()
        rotvec[0] = 0.
        rotvec[2] = 0.
        pose.rot = SO3.from_rotvec(rotvec)
        pose.trans[1] = 0. # xz constr
        tire.set_pose(pose)

world.set_step_callback(cb)
body1 = eb.Box.create("tire1", world, [0.05, 0.05, 0.05])
body2 = eb.Box.create("tire2", world, [0.05, 0.05, 0.05])


body1.set_pose(SE3(trans=[0,0,0.2]))
body2.set_pose(SE3(trans=[0.1,0,0.3]))

while True:
    world.step()