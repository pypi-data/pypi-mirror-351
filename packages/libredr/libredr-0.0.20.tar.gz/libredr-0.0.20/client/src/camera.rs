use nalgebra as na;
use pyo3::prelude::*;
use ndarray::{Axis, Array3};
use anyhow::{Result, anyhow, ensure};
use numpy::{PyReadonlyArray1, PyArray2, ToPyArray, PyUntypedArrayMethods};

mod orthogonal;
mod perspective;

const EPS: f32 = 1e-6;

/// Orthogonal camera model (Rust and Python)
pub use self::orthogonal::{orthogonal_ray, py_orthogonal_ray};
/// Perspective camera model (Rust and Python)
pub use self::perspective::{perspective_ray, py_perspective_ray};

/// Convert `ray_corner` (6, height + 1, width + 1) to `ray` (18, height, width)
/// Camera model use x-right, y-down, z-forward axis scheme
fn from_ray_corner(ray_corner: Array3<f32>) -> Result<Array3<f32>> {
  ensure!(ray_corner.shape()[1] > 1);
  ensure!(ray_corner.shape()[2] > 1);
  let mut ray = Array3::zeros((18, ray_corner.shape()[1] - 1, ray_corner.shape()[2] - 1));
  ray.axis_iter_mut(Axis(2)).enumerate().for_each(|(x, mut ray)| {
    ray.axis_iter_mut(Axis(1)).enumerate().for_each(|(y, mut ray)| {
      for i in 0..3 {
        ray[i] = ray_corner[(i, y, x)];
        ray[i + 3] = ray_corner[(i, y, x + 1)] - ray_corner[(i, y, x)];
        ray[i + 6] = ray_corner[(i, y + 1, x)] - ray_corner[(i, y, x)];
        ray[i + 9] = ray_corner[(i + 3, y, x)];
        ray[i + 12] = ray_corner[(i + 3, y, x + 1)] - ray_corner[(i + 3, y, x)];
        ray[i + 15] = ray_corner[(i + 3, y + 1, x)] - ray_corner[(i + 3, y, x)];
      }
    });
  });
  Ok(ray)
}

/// Construct 4 * 4 extrinsic matrix from `position`, `look_at`, `up` vectors
pub fn look_at_extrinsic(
    position: na::VectorView3<f32>,
    look_at: na::VectorView3<f32>,
    up: na::VectorView3<f32>) -> Result<na::Matrix4<f32>> {
  ensure!(position.fold(true, |acc, v| { acc && v.is_finite() }),
          "camera::look_at_extrinsic: `position` is not finite");
  ensure!(look_at.fold(true, |acc, v| { acc && v.is_finite() }),
          "camera::look_at_extrinsic: `look_at` is not finite");
  ensure!(up.fold(true, |acc, v| { acc && v.is_finite() }),
          "camera::look_at_extrinsic: `up` is not finite");
  let d = (look_at - position).try_normalize(EPS).ok_or(anyhow!("camera::look_at_extrinsic: `d` is 0"))?;
  let right = d.cross(&up).try_normalize(EPS).ok_or(anyhow!("camera::look_at_extrinsic: `right` is 0"))?;
  let down = d.cross(&right).normalize();
  let rotation = na::Matrix3::from_rows(&[right.transpose(), down.transpose(), d.transpose()]).to_homogeneous();
  let translation = na::Matrix4::new_translation(&-position);
  Ok(rotation * translation)
}

/// Python version [`look_at_extrinsic`]
/// Return matrix is F-contiguous (column first order)
#[pyfunction]
#[pyo3(name = "look_at_extrinsic")]
pub fn py_look_at_extrinsic<'py>(
    py: Python<'py>,
    position: PyReadonlyArray1<f32>,
    look_at: PyReadonlyArray1<f32>,
    up: PyReadonlyArray1<f32>) -> PyResult<Bound<'py, PyArray2<f32>>> {
  let position = position.try_as_matrix().ok_or(
    anyhow!("camera::look_at_extrinsic: `position` expected shape {:?}, found {:?}", [3], position.shape()))?;
  let look_at = look_at.try_as_matrix().ok_or(
    anyhow!("camera::look_at_extrinsic: `look_at` expected shape {:?}, found {:?}", [3], look_at.shape()))?;
  let up = up.try_as_matrix().ok_or(
    anyhow!("camera::look_at_extrinsic: `up` expected shape {:?}, found {:?}", [3], up.shape()))?;
  let extrinsic = look_at_extrinsic(position, look_at, up)?;
  Ok(extrinsic.to_pyarray(py))
}

/// All camera models (Python)
pub fn py_camera<'py>(py: Python<'py>, parent_module: &Bound<'py, PyModule>) -> PyResult<()> {
  let module = PyModule::new(py, "camera")?;
  module.add_function(wrap_pyfunction!(py_look_at_extrinsic, &module)?)?;
  module.add_function(wrap_pyfunction!(py_orthogonal_ray, &module)?)?;
  module.add_function(wrap_pyfunction!(py_perspective_ray, &module)?)?;
  parent_module.add_submodule(&module)?;
  Ok(())
}
