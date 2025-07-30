import torch
import torch.nn.functional as F


def cubemap_pad(input, pad):
  '''
  Use adjoint faces to pad cubemap projected panoramic images
  # Arguments
  * `input`: (N, 6, C, H, H)
  * `pad`: int
  Cubemap projection scheme is according to `libredr.camera.cube`
  '''
  assert(len(input.shape) == 5)
  assert(input.shape[1] == 6)
  assert(input.shape[3] == input.shape[4])
  input = input.flip(dims=[-2])
  input_pad = F.pad(input, [pad] * 4)
  input_pad[:, 0, :, pad:-pad, -pad:] = input[:, 2, :, :, -pad:].flip(dims=[-1])
  input_pad[:, 0, :, pad:-pad,  :pad] = input[:, 3, :, :, -pad:]
  input_pad[:, 0, :, -pad:, pad:-pad] = input[:, 4, :, :, -pad:].mT.flip(dims=[-2])
  input_pad[:, 0, :,  :pad, pad:-pad] = input[:, 5, :, :, -pad:].mT
  input_pad[:, 1, :, pad:-pad, -pad:] = input[:, 2, :, :, :pad]
  input_pad[:, 1, :, pad:-pad,  :pad] = input[:, 3, :, :, :pad].flip(dims=[-1])
  input_pad[:, 1, :, -pad:, pad:-pad] = input[:, 4, :, :, :pad].mT
  input_pad[:, 1, :,  :pad, pad:-pad] = input[:, 5, :, :, :pad].mT.flip(dims=[-2])
  input_pad[:, 2, :, pad:-pad, -pad:] = input[:, 0, :, :, -pad:].flip(dims=[-1])
  input_pad[:, 2, :, pad:-pad,  :pad] = input[:, 1, :, :, -pad:]
  input_pad[:, 2, :, -pad:, pad:-pad] = input[:, 4, :, -pad:, :].flip(dims=[-2])
  input_pad[:, 2, :,  :pad, pad:-pad] = input[:, 5, :, -pad:, :]
  input_pad[:, 3, :, pad:-pad, -pad:] = input[:, 0, :, :, :pad]
  input_pad[:, 3, :, pad:-pad,  :pad] = input[:, 1, :, :, :pad].flip(dims=[-1])
  input_pad[:, 3, :, -pad:, pad:-pad] = input[:, 4, :, :pad, :]
  input_pad[:, 3, :,  :pad, pad:-pad] = input[:, 5, :, :pad, :].flip(dims=[-2])
  input_pad[:, 4, :, pad:-pad, -pad:] = input[:, 0, :, -pad:, :].mT.flip(dims=[-1])
  input_pad[:, 4, :, pad:-pad,  :pad] = input[:, 1, :, -pad:, :].mT
  input_pad[:, 4, :, -pad:, pad:-pad] = input[:, 2, :, -pad:, :].flip(dims=[-2])
  input_pad[:, 4, :,  :pad, pad:-pad] = input[:, 3, :, -pad:, :]
  input_pad[:, 5, :, pad:-pad, -pad:] = input[:, 0, :, :pad, :].mT
  input_pad[:, 5, :, pad:-pad,  :pad] = input[:, 1, :, :pad, :].mT.flip(dims=[-1])
  input_pad[:, 5, :, -pad:, pad:-pad] = input[:, 2, :, :pad:, :]
  input_pad[:, 5, :,  :pad, pad:-pad] = input[:, 3, :, :pad:, :].flip(dims=[-2])
  input_pad = input_pad.flip(dims=[-2])
  return input_pad


def __test__():
  import cv2 as cv
  import numpy as np
  from libredr.camera import cube_ray
  image = cube_ray(128, np.eye(4))[9:12] * 0.5 + 0.5
  print("image", image.shape)
  image = torch.tensor(image).permute(1, 0, 2, 3)[None, ...]
  print("image", image.shape)
  image_pad = cubemap_pad(image, 10)
  print("image_pad", image_pad.shape)
  for i in range(6):
    cv.imshow(f"image_{i}", image[0, i, ...].numpy().transpose(1, 2, 0))
    cv.imshow(f"image_pad_{i}", image_pad[0, i, ...].numpy().transpose(1, 2, 0))
  cv.waitKey(0)


if __name__ == "__main__":
  __test__()
