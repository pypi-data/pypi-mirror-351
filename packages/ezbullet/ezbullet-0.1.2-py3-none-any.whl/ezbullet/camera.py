import numpy as np
import pybullet as p
from attrs import define
from ezpose import SE3, SO3
from numpy.typing import ArrayLike

from .world import World


@define
class CameraIntrinsic:
    width: float
    height: float
    fx: float
    fy: float
    cx: float
    cy: float
    near: float
    far: float

    def get_projection_matrix(self):
        fx, fy = self.fx, self.fy
        cx, cy = self.cx, self.cy
        return np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    def get_projection_matrix_opengl(self):
        w, h = self.width, self.height
        fx, fy = self.fx, self.fy
        cx, cy = self.cx, self.cy
        near, far = self.near, self.far

        x_scale = 2 / w * fx
        y_scale = 2 / h * fy
        x_shift = 1 - 2 * cx / w
        y_shift = (2 * cy - h) / h
        return np.array(
            [
                [x_scale, 0, x_shift, 0],
                [0, y_scale, y_shift, 0],
                [0, 0, (near + far) / (near - far), 2 * near * far / (near - far)],
                [0, 0, -1, 0],
            ]
        ).flatten(order="F")

    def depth_to_points(self, depth, eps=0.01):
        height, width = depth.shape
        X, Y = np.meshgrid(np.arange(width), np.arange(height), indexing="xy")
        pixels = np.stack([X, Y]).reshape(2, -1)
        pixels_homo_coord = np.vstack([pixels, np.ones(pixels.shape[1])])
        P_inv = np.linalg.inv(self.get_projection_matrix())
        obj_pixels_norm = (P_inv @ pixels_homo_coord).T
        points_cam = np.einsum("ij,i->ij", obj_pixels_norm, depth.flatten())
        is_valid = (self.near + eps <= depth) & (depth <= self.far - eps)
        return points_cam[is_valid.flatten()]


@define
class Camera:
    world: World
    intrinsic: CameraIntrinsic

    @staticmethod
    def get_look_at_pose(
        eye_pos: ArrayLike, target_pos=np.zeros(3), up_vector=np.array([0.0, 0, 1])
    ):
        f = np.asarray(target_pos) - np.asarray(eye_pos)
        f /= np.linalg.norm(f)
        s = np.cross(f, up_vector)
        s /= np.linalg.norm(s)
        u = np.cross(s, f)
        rot_mat = np.vstack([s, -u, f]).T
        t = np.asarray(eye_pos)
        return SE3(SO3.from_matrix(rot_mat), t)

    def render(self, cam_pose: SE3, render_mode="tiny"):
        """output: rgb, depth, seg"""
        cam_pose_opengl = cam_pose @ SE3(SO3.from_euler("xyz", [np.pi, 0, 0]))
        view_matrix = list(cam_pose_opengl.inv().as_matrix().flatten("F"))
        proj_matrix = list(self.intrinsic.get_projection_matrix_opengl())

        # result: (width, height, rgb, depth, seg)
        renderer = (
            p.ER_BULLET_HARDWARE_OPENGL if render_mode != "tiny" else p.ER_TINY_RENDERER
        )
        result = self.world.getCameraImage(
            width=self.intrinsic.width,
            height=self.intrinsic.height,
            viewMatrix=view_matrix,
            projectionMatrix=proj_matrix,
            renderer=renderer,
        )
        w, h = self.intrinsic.width, self.intrinsic.height
        far, near = self.intrinsic.far, self.intrinsic.near
        rgb = np.reshape(result[2], (h, w, 4))[:, :, :3] * 1.0 / 255.0
        depth = np.asarray(result[3]).reshape(h, -1)
        seg = np.asarray(result[4])
        depth = far * near / (far - (far - near) * depth)
        return rgb, depth, seg


# # add noise to depth image
# def add_depth_noise(
#     depth,
#     noise_std=0.,
#     inlier_distance=0.05,
#     thres=0.5,
#     size_filt=None,
#     device="cpu"
# ):
#     import torch
#     to_tensor = lambda x, device: torch.tensor(x, device=device, dtype=torch.float32)
#     to_numpy = lambda x: x.detach().cpu().numpy()

#     def _add_gaussian_shifts(depth, std=1.):
#         depth_ = to_tensor(depth, device) # torch.tensor(depth).float().to(device)
#         depth_ = depth_.unsqueeze(0).unsqueeze(0)
#         r, c = depth.shape

#         rr = torch.arange(r, device=device)
#         cc = torch.arange(c, device=device)
#         grid_y, grid_x = torch.meshgrid(rr, cc, indexing="ij")
#         grid = torch.stack([grid_x, grid_y], dim=-1).float()
#         grid += torch.randn(r, c, 2, device=device) * std

#         grid[..., 0].clamp_(0, c-1)
#         grid[..., 1].clamp_(0, r-1)

#         n_grid = 2 * grid / torch.tensor([c-1, r-1], device=device) - 1
#         n_grid = n_grid.unsqueeze(0)
#         shifted_depth = torch.nn.functional.grid_sample(
#             depth_, n_grid,
#             mode="bilinear", padding_mode="zeros", align_corners=True)
#         return to_numpy(shifted_depth.squeeze())

#     def _simulate_depth_shade(depth, size_filt=5, window_inlier_distance=0.05, thres=0.5):
#         INVALID_VAL = 2.
#         depth_ = to_tensor(depth, device)
#         pad_size = center = size_filt // 2

#         # unfold image to work with GPU
#         depth_padded = torch.nn.functional.pad(depth_, (pad_size, pad_size, pad_size, pad_size), mode="constant", value=INVALID_VAL)
#         depth_padded = depth_padded.unsqueeze(0).unsqueeze(0)
#         unfold = torch.nn.Unfold(kernel_size=(size_filt, size_filt))
#         depth_unfolded = unfold(depth_padded)
#         depth_unfolded = depth_unfolded.squeeze(0)

#         # ignore if center pixel is outlier
#         depth_center = depth_unfolded[center*size_filt + center, :]
#         center_valid_mask = depth_center < INVALID_VAL
#         n_valids = (depth_unfolded < INVALID_VAL).sum(dim=0)
#         total_valid_mask = n_valids > (size_filt * size_filt)*thres

#         # remove if the kernel deviates a lot
#         valid_mask_elementwise = (depth_unfolded < INVALID_VAL)
#         depth_unfolded_nan = depth_unfolded.clone()
#         depth_unfolded_nan[~valid_mask_elementwise] = torch.nan
#         center = torch.nanmean(depth_unfolded_nan, dim=0)
#         diffs = torch.abs(depth_unfolded - center)
#         valids = diffs < window_inlier_distance
#         n_valids = valids.sum(dim=0).float()
#         inlier_mask = n_valids > (size_filt * size_filt)*thres

#         # update final result
#         out_depth = torch.full_like(depth_, INVALID_VAL, device=device)
#         valid_mask = center_valid_mask & total_valid_mask & inlier_mask
#         accu = depth_center[valid_mask] #torch.round(depth_center[valid_mask]*8)/8.
#         out_depth_flat = out_depth.view(-1)
#         out_depth_flat[valid_mask] = accu
#         return to_numpy(out_depth)

#     if size_filt is None:
#         size_filt = np.random.choice([3, 5, 7, 9])
#     if noise_std != 0.:
#         depth = _add_gaussian_shifts(depth, std=noise_std/2)
#     depth = _simulate_depth_shade(
#         depth, size_filt=size_filt-2,
#         window_inlier_distance=0.1,
#         thres=thres/2)

#     if noise_std != 0.:
#         depth = _add_gaussian_shifts(depth, std=noise_std)
#     depth = _simulate_depth_shade(
#         depth, size_filt=size_filt,
#         window_inlier_distance=inlier_distance,
#         thres=thres)
#     return depth
