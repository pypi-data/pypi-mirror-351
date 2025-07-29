from __future__ import annotations

# from .utils import generate_temp_urdf
from pathlib import Path

import trimesh
from attrs import define
from ezpose import SE3
from numpy.typing import ArrayLike

from .shape import ShapeBase, SphereShape, CylinderShape, BoxShape, MeshShape
from .world import Body, World


@define
class GeometryBase(Body):
    shape: ShapeBase

    @classmethod
    def make_geometry_body(
        cls,
        name: str,
        world: World,
        vis_id: int,
        col_id: int,
        mass: float,
        shape: ShapeBase,
    ):
        if name in world.bodies:
            print("Body name already exists.")
            return world.bodies[name]

        uid = world.createMultiBody(
            baseVisualShapeIndex=vis_id, 
            baseCollisionShapeIndex=col_id, 
            baseMass=mass
        )
        body = cls(
            world=world, uid=uid, name=name, mass=mass, ghost=shape.ghost, shape=shape
        )
        world.bodies[name] = body
        return body


@define(repr=False)
class Sphere(GeometryBase):
    @classmethod
    def create(
        cls,
        name: str,
        world: World,
        radius: float,
        mass: float = 0.5,
        rgba: tuple[float] = (1, 0, 0, 1),
        ghost: bool = False,
    ):
        shape = SphereShape(rgba=rgba, ghost=ghost, radius=radius)
        vis_id, col_id = world.get_shape_id(shape)
        return cls.make_geometry_body(name, world, vis_id, col_id, mass, shape)


@define(repr=False)
class Cylinder(GeometryBase):
    @classmethod
    def create(
        cls,
        name: str,
        world: World,
        radius: float,
        length: float,
        mass: float = 0.5,
        rgba: tuple[float] = (1, 0, 0, 1),
        offset: SE3 = SE3.identity(),
        ghost: bool = False,
    ):
        shape = CylinderShape(
            rgba=rgba,
            ghost=ghost,
            radius=radius,
            length=length,
            offset=offset,
        )
        vis_id, col_id = world.get_shape_id(shape)
        return cls.make_geometry_body(name, world, vis_id, col_id, mass, shape)


@define(repr=False)
class Box(GeometryBase):
    @classmethod
    def create(
        cls,
        name: str,
        world: World,
        half_extents: ArrayLike,
        mass: float = 0.5,
        rgba: tuple[float] = (1, 1, 1, 1),
        ghost: bool = False,
    ):
        shape = BoxShape(rgba=rgba, ghost=ghost, half_extents=half_extents)
        vis_id, col_id = world.get_shape_id(shape)
        return cls.make_geometry_body(name, world, vis_id, col_id, mass, shape)


@define(repr=False)
class Mesh(GeometryBase):
    @classmethod
    def create(
        cls,
        name: str,
        world: World,
        visual_mesh_path: str | Path | None,
        col_mesh_path: str | Path | None = None,
        offset: SE3 = None,
        scale: float = 1.0,
        mass: float = 0.5,
        rgba: tuple[float] = (1, 1, 1, 1),
    ):
        """We assume that visual mesh is in the same coordinate as collision mesh"""
        # i think centering should be dealt with mesh level
        # centering_type:str|None = "bb", # bb(bounding box center), centroid, None
        # center = Mesh.get_center(visual_mesh_path, centering_type, scale=scale)
        # offset = SE3(trans=-center)  #in pybullet, scale is applied first
        if offset is None:
            offset = SE3()
        ghost = True if col_mesh_path is None else False
        shape = MeshShape(
            visual_mesh_path=visual_mesh_path,
            col_mesh_path=col_mesh_path,
            offset=offset,
            scale=scale,
            rgba=rgba,
            ghost=ghost,
        )
        vis_id, col_id = world.get_shape_id(shape)
        return cls.make_geometry_body(name, world, vis_id, col_id, mass, shape)

    def as_trimesh(self, is_col: bool = False):
        """if is_col is True, return the collision mesh, else return the visual mesh"""
        shape: MeshShape = self.shape
        mesh_path = shape.visual_mesh_path

        if is_col:
            assert shape.col_mesh_path is not None, "No collision mesh"
            mesh_path = shape.col_mesh_path
        return (
            trimesh.load(mesh_path)
            .apply_translation(shape.offset.trans / shape.scale)
            .apply_scale(shape.scale)
        )

    @classmethod
    def from_trimesh(
        cls,
        name,
        world: World,
        mesh: trimesh.Trimesh,
        col_mesh: trimesh.Trimesh | None = None,
        mass: float = 0.5,
        rgba: ArrayLike = [1, 1, 1, 1],
        offset: SE3 = None,
        # centering_type=None,
    ):
        if offset is None:
            offset = SE3()
        import tempfile

        tempdir = tempfile.TemporaryDirectory()
        if col_mesh is None:
            col_mesh = mesh

        mesh_path = Path(tempdir.name) / "mesh.obj"
        col_mesh_path = Path(tempdir.name) / "col_mesh.obj"
        mesh.export(mesh_path, "obj")
        col_mesh.export(col_mesh_path, "obj")
        obj = cls.create(
            name,
            world,
            str(mesh_path),
            str(col_mesh_path),
            offset=offset,
            # centering_type=centering_type,
            mass=mass,
            rgba=rgba,
        )
        tempdir.cleanup()
        return obj
