import numpy as np
import pybullet as p
from attrs import Factory, define, field
from ezpose import SE3


@define
class ShapeBase:
    rgba: tuple = (1, 1, 1, 1)
    ghost: bool = True
    offset: SE3 = Factory(SE3)

    def get_viz_query(self) -> dict:
        return dict(
            visualFramePosition=self.offset.trans,
            visualFrameOrientation=self.offset.rot.as_quat(),
            rgbaColor=self.rgba,
        )

    def get_col_query(self):
        return dict(
            collisionFramePosition=self.offset.trans,
            collisionFrameOrientation=self.offset.rot.as_quat(),
        )

    def __eq__(self, other):
        d1 = {**self.get_viz_query(), **self.get_col_query()}
        d2 = {**other.get_viz_query(), **other.get_col_query()}
        return all(
            [
                d1[k] == d2[k]
                if not isinstance(d1[k], np.ndarray)
                else np.allclose(d1[k], d2[k])
                for k in d1.keys()
            ]
        )

    def __hash__(self):
        d = {**self.get_viz_query(), **self.get_col_query()}
        s = str({k: d[k] for k in d.keys()})
        return s.__hash__()


@define(frozen=True, kw_only=True)
class SphereShape(ShapeBase):
    radius: float

    def get_viz_query(self):
        query = super().get_viz_query()
        query.update(shapeType=p.GEOM_SPHERE, radius=self.radius)
        return query

    def get_col_query(self):
        query = super().get_col_query()
        query.update(shapeType=p.GEOM_SPHERE, radius=self.radius)
        return query

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


@define(frozen=True, kw_only=True)
class CylinderShape(ShapeBase):
    radius: float
    length: float

    def get_viz_query(self):
        query = super().get_viz_query()
        query.update(
            shapeType=p.GEOM_CYLINDER,
            radius=self.radius,
            length=self.length,
        )
        return query

    def get_col_query(self):
        query = super().get_col_query()
        query.update(
            shapeType=p.GEOM_CYLINDER,
            radius=self.radius,
            height=self.length,
        )
        return query

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


@define(frozen=True, kw_only=True)
class BoxShape(ShapeBase):
    half_extents: tuple[float] = field(converter=tuple)

    def get_viz_query(self):
        query = super().get_viz_query()
        query.update(
            shapeType=p.GEOM_BOX,
            halfExtents=self.half_extents,
        )
        return query

    def get_col_query(self):
        query = super().get_col_query()
        query.update(
            shapeType=p.GEOM_BOX,
            halfExtents=self.half_extents,
        )
        return query

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


@define(frozen=True, kw_only=True)
class MeshShape(ShapeBase):
    visual_mesh_path: str = field(converter=str)
    col_mesh_path: str = field(converter=str)
    scale: float

    def get_viz_query(self):
        query = super().get_viz_query()
        query.update(
            shapeType=p.GEOM_MESH,
            fileName=self.visual_mesh_path,
            meshScale=np.ones(3) * self.scale,
        )
        return query

    def get_col_query(self):
        query = super().get_col_query()
        query.update(
            shapeType=p.GEOM_MESH,
            fileName=self.col_mesh_path,
            meshScale=np.ones(3) * self.scale,
        )
        return query

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()
