import torch

def gaussian_directional_envmap(resolution, direction, intensity, alpha, device=None):
  '''
  PyTorch function to construct differentiable `envmap` from `direction`
  # Arguments
  * `resolution`: 1 integer
  * `direction`: float tensor of size (3) or (`batch_size`, 3)
  * `intensity`: float tensor of size (3) or (`batch_size`, 3)
  * `alpha`: float tensor
  # Return
  * (`batch_size`, 3, 6, `resolution`, `resolution`)
  '''
  axis_xyz = torch.zeros([6, resolution + 1, resolution + 1, 3], dtype=torch.float32, device=device)
  axis_xyz[0,:,:, 0] = 1.
  axis_xyz[1,:,:, 0] = -1.
  axis_xyz[0:2,:,:, 2] = torch.linspace(-1, 1, resolution + 1, dtype=torch.float32, device=device)[None,:, None]
  axis_xyz[0:2,:,:, 1] = torch.linspace(-1, 1, resolution + 1, dtype=torch.float32, device=device)[None, None,:]
  axis_xyz[2,:,:, 1] = 1.
  axis_xyz[3,:,:, 1] = -1.
  axis_xyz[2:4,:,:, 2] = torch.linspace(-1, 1, resolution + 1, dtype=torch.float32, device=device)[None,:, None]
  axis_xyz[2:4,:,:, 0] = torch.linspace(-1, 1, resolution + 1, dtype=torch.float32, device=device)[None, None,:]
  axis_xyz[4,:,:, 2] = 1.
  axis_xyz[5,:,:, 2] = -1.
  axis_xyz[4:6,:,:, 1] = torch.linspace(-1, 1, resolution + 1, dtype=torch.float32, device=device)[None,:, None]
  axis_xyz[4:6,:,:, 0] = torch.linspace(-1, 1, resolution + 1, dtype=torch.float32, device=device)[None, None,:]
  axis_xyz = (axis_xyz[:, :-1, :-1, ...] + \
              axis_xyz[:, :-1,  1:, ...] + \
              axis_xyz[:,  1:, :-1, ...] + \
              axis_xyz[:,  1:,  1:, ...]) / 4
  axis_xyz = axis_xyz.flip(1)
  axis_xyz = axis_xyz / torch.linalg.norm(axis_xyz, dim=-1, keepdim=True)
  direction = direction / torch.linalg.norm(direction, dim=-1, keepdim=True)
  envmap = torch.nn.functional.relu((axis_xyz * direction[..., None, None, None, :]).sum(dim=-1)).pow(alpha)
  envmap = envmap[..., None, :, :, :].repeat(*[1] * (len(direction.shape) - 1), 3, 1, 1, 1)
  envmap = envmap * intensity[..., :, None, None, None]
  return envmap
