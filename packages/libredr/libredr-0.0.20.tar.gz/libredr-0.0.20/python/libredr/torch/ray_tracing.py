import copy
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor
import torch
import numpy as np
import torch.nn as nn

class RayTracingFunction(torch.autograd.Function):
  '''
  PyTorch autograd function to render a image
  Only calculate gradient w.r.t. `ray`, `texture`, and `envmap`
  '''
  @staticmethod
  def forward(ctx, client, render_config, geometry, ray, texture, envmap):
    device = ray.device
    ctx.client = client
    render_config = copy.deepcopy(render_config)
    render_config["requires_grad"] = ray.requires_grad or texture.requires_grad or envmap.requires_grad
    ctx.render_config = render_config
    ray = ray.detach().cpu().numpy()
    texture = texture.detach().cpu().numpy()
    envmap = envmap.detach().cpu().numpy()
    # print("forward ray", ray.shape)
    # print("forward texture", texture.shape)
    # print("forward envmap", envmap.shape)
    render = client.ray_tracing_forward(
      geometry = geometry,
      ray = ray,
      texture = texture,
      envmap = envmap,
      **render_config)
    return torch.tensor(render, device=device)

  @staticmethod
  def backward(ctx, d_render):
    device = d_render.device
    client = ctx.client
    render_config = ctx.render_config
    d_render = d_render.detach()[0:3, ...].cpu().numpy()
    # print("backward d_render", d_render.shape)
    d_texture, d_envmap, d_ray_texture = client.ray_tracing_backward(d_render)
    d_texture = torch.tensor(d_texture, device=device)
    d_envmap = torch.tensor(d_envmap, device=device)
    if d_ray_texture is not None:
      d_ray_texture = np.pad(d_ray_texture, ((19, 0),) + ((0, 0),) * (len(d_ray_texture.shape) - 1))
      d_ray_texture = torch.tensor(d_ray_texture, device=device)
    return None, None, None, d_ray_texture, d_texture, d_envmap


class RayTracing(nn.Module):
  '''
  PyTorch module to render a scene
  Surface normal in `ray` and `texture` are normalized before calling `RayTracingFunction`
  '''
  def __init__(self, client):
    '''
    Set LibreDR client to run render
    Client is constructed using `libredr.LibreDR`
    '''
    super().__init__()
    self.client = client

  def forward(self, geometry, ray, texture, envmap, **render_config):
    '''
    See `libredr.LibreDR.ray_tracing_forward` for arguments definition
    '''
    if render_config["camera_space"]:
      ray = torch.cat((
        ray[:19, ...],
        ray[19:22, ...] / torch.linalg.norm(ray[19:22, ...], ord=2, dim=0, keepdim=True) + 1e-6,
        ray[22:, ...],
      ))
    texture = torch.cat((
      texture[0:3, ...] / torch.linalg.norm(texture[0:3, ...], ord=2, dim=0, keepdim=True) + 1e-6,
      texture[3:, ...],
    ))
    return RayTracingFunction.apply(self.client, render_config, geometry, ray, texture, envmap)


class PoolRayTracingFunction(torch.autograd.Function):
  @staticmethod
  def forward(ctx, pool, clients, render_config, geometry, ray, texture, envmap):
    n_batch = len(geometry)
    assert(len(clients) >= n_batch)
    assert(ray.shape[0] == n_batch)
    assert(texture.shape[0] == n_batch)
    assert(envmap.shape[0] == n_batch)
    ctx.pool = pool
    ctx.pool_ctx = [Namespace() for i_batch in range(n_batch)]
    ctx.render_config = render_config
    args = []
    for i_batch in range(n_batch):
      args.append({
        "geometry": geometry[i_batch],
        "ray": ray[i_batch],
        "texture": texture[i_batch],
        "envmap": envmap[i_batch],
        **render_config})
    pool_forward = lambda i_batch: RayTracingFunction.forward(
      ctx.pool_ctx[i_batch], clients[i_batch], render_config,
      geometry[i_batch], ray[i_batch, ...], texture[i_batch, ...], envmap[i_batch, ...])
    return torch.stack(tuple(pool.map(pool_forward, range(n_batch))))

  @staticmethod
  def backward(ctx, d_render):
    n_batch = len(ctx.pool_ctx)
    pool_backward = lambda i_batch: RayTracingFunction.backward(ctx.pool_ctx[i_batch], d_render[i_batch, ...])
    _, _, _, d_ray_texture, d_texture, d_envmap = zip(*ctx.pool.map(pool_backward, range(n_batch)))
    if ctx.render_config["camera_space"]:
      d_ray_texture = torch.stack(d_ray_texture)
    else:
      d_ray_texture = None
    d_texture = torch.stack(d_texture)
    d_envmap = torch.stack(d_envmap)
    return None, None, None, None, d_ray_texture, d_texture, d_envmap


class PoolRayTracing(nn.Module):
  '''
  PyTorch module to render a batch of scenes using `ThreadPoolExecutor`
  Surface normal in `ray` and `texture` are normalized before calling `RayTracingFunction`
  '''
  def __init__(self, clients, max_workers=None):
    '''
    Set LibreDR clients and the number of workers to run render
    Clients are constructed using `libredr.LibreDR`
    The number of clients must be larger or equal to batch size
    If `max_workers` is None or not given, use the number of clients for thread pool
    '''
    super().__init__()
    self.clients = clients
    if max_workers is None:
      max_workers = len(clients)
    self.pool = ThreadPoolExecutor(max_workers)

  def forward(self, geometry, ray, texture, envmap, **render_config):
    '''
    See `libredr.LibreDR.ray_tracing_forward` for arguments definition
    `geometry`, `ray`, `texture`, and `envmap` are batched
    '''
    if render_config["camera_space"]:
      ray = torch.cat((
        ray[:, :19, ...],
        ray[:, 19:22, ...] / torch.linalg.norm(ray[:, 19:22, ...], ord=2, dim=1, keepdim=True) + 1e-6,
        ray[:, 22:, ...],
      ), dim=1)
    texture = torch.cat((
      texture[:, 0:3, ...] / torch.linalg.norm(texture[:, 0:3, ...], ord=2, dim=1, keepdim=True) + 1e-6,
      texture[:, 3:, ...],
    ), dim=1)
    return PoolRayTracingFunction.apply(self.pool, self.clients, render_config, geometry, ray, texture, envmap)
