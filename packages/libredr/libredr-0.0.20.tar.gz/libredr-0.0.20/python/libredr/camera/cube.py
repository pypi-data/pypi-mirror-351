import numpy as np

def cube_ray(resolution, extrinsic):
  '''
  Construct input ray for cubic unwrapped panoramic camera model
  # Arguments
  * `resolution`: a single integer
  * `extrinsic`: 4 * 4 matrix
  # Return
  * 18 * 6 * `resolution` * `resolution`
  Camera model use x-right, y-down, z-forward axis scheme
  '''
  axis_xyz = np.zeros([6, resolution + 1, resolution + 1, 3], dtype=np.float32)
  axis_xyz[0,:,:, 0] = 1.
  axis_xyz[1,:,:, 0] = -1.
  axis_xyz[0:2,:,:, 2] = np.linspace(-1, 1, resolution + 1)[np.newaxis,:, np.newaxis]
  axis_xyz[0:2,:,:, 1] = np.linspace(-1, 1, resolution + 1)[np.newaxis, np.newaxis,:]
  axis_xyz[2,:,:, 1] = 1.
  axis_xyz[3,:,:, 1] = -1.
  axis_xyz[2:4,:,:, 2] = np.linspace(-1, 1, resolution + 1)[np.newaxis,:, np.newaxis]
  axis_xyz[2:4,:,:, 0] = np.linspace(-1, 1, resolution + 1)[np.newaxis, np.newaxis,:]
  axis_xyz[4,:,:, 2] = 1.
  axis_xyz[5,:,:, 2] = -1.
  axis_xyz[4:6,:,:, 1] = np.linspace(-1, 1, resolution + 1)[np.newaxis,:, np.newaxis]
  axis_xyz[4:6,:,:, 0] = np.linspace(-1, 1, resolution + 1)[np.newaxis, np.newaxis,:]
  axis_xyz = axis_xyz[:, ::-1, :, :]
  axis_xyz = np.stack([axis_xyz[..., 0], -axis_xyz[..., 2], axis_xyz[..., 1]], axis=-1)
  extrinsic_inv = np.linalg.inv(extrinsic)
  # print('axis_xyz', axis_xyz.shape)
  ret_rd = np.matmul(extrinsic_inv[:3,:3], axis_xyz[..., np.newaxis]).squeeze(-1)
  ret_rd = np.concatenate([ret_rd[:,:-1,:-1, ...],
    ret_rd[:,:-1, 1:, ...] - ret_rd[:,:-1,:-1, ...],
    ret_rd[:, 1:,:-1, ...] - ret_rd[:,:-1,:-1, ...]], axis=-1)
  ret_rd = ret_rd.transpose(3, 0, 1, 2)
  ret_r = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)[:, np.newaxis]
  ret_r = np.matmul(extrinsic_inv, ret_r)[:3, np.newaxis,:, np.newaxis]
  ret_r = np.broadcast_to(ret_r, (3, 6, resolution, resolution))
  ret_r = np.concatenate([ret_r] + [np.zeros_like(ret_r)] * 2, axis=0)
  return np.concatenate([ret_r, ret_rd], axis=0)
