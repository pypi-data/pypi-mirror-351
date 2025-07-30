import os
import sys
__all__ = ["camera", "light_source", "LibreDR", "Geometry"]
# All camera models (Python)
from . import camera
# LibreDR client (Rust)
from .libredr import __author__, __version__, LibreDR, Geometry
# All light source models (Rust)
from .libredr import light_source
# All camera models (Ruse)
from .libredr import camera as camera_rust
camera.orthogonal_ray = camera_rust.orthogonal_ray
camera.perspective_ray = camera_rust.perspective_ray
camera.look_at_extrinsic = camera_rust.look_at_extrinsic
# PyTorch bindings (Python)
try:
  import torch as _torch
except ModuleNotFoundError:
  if "LIBREDR_LOG_LEVEL" in os.environ and os.environ["LIBREDR_LOG_LEVEL"] in ("info", "debug"):
    print("PyTorch not found, disabled PyTorch bindings.")
if "torch" in sys.modules:
  from . import torch
  __all__.append("torch")
