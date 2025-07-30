use std::cmp::max;
use nalgebra as na;
use pyo3::prelude::*;
use ndarray::{Axis, Array1, Array3};
use anyhow::{Result, anyhow, ensure};
use numpy::{PyReadonlyArray2, PyArray3, IntoPyArray, PyUntypedArrayMethods};
use super::from_ray_corner;

/// Construct input ray for perspective camera model
/// # Arguments
/// * `resolution`: tuple of 2 usize [`width`, `height`]
/// * `intrinsic`: 3 * 3 matrix
/// * `extrinsic`: 4 * 4 matrix
/// # Return
/// * 18 * `height` * `width`
/// Camera model use x-right, y-down, z-forward axis scheme
pub fn perspective_ray(
    resolution: &[usize; 2],
    intrinsic: na::MatrixView<f32, na::Const<3>, na::Const<3>, na::Dyn, na::Dyn>,
    extrinsic: na::MatrixView<f32, na::Const<4>, na::Const<4>, na::Dyn, na::Dyn>) -> Result<Array3<f32>> {
  ensure!(intrinsic.fold(true, |acc, v| { acc && v.is_finite() }),
          "camera::perspective_ray: `intrinsic` is not finite");
  ensure!(extrinsic.fold(true, |acc, v| { acc && v.is_finite() }),
          "camera::perspective_ray: `extrinsic` is not finite");
  let intrinsic_inv = intrinsic.try_inverse().ok_or(anyhow!("camera::perspective_ray: `intrinsic` is not invertible"))?;
  let extrinsic_inv = extrinsic.try_inverse().ok_or(anyhow!("camera::perspective_ray: `extrinsic` is not invertible"))?;
  let resolution_max = max(resolution[0], resolution[1]);
  let axis_range = [resolution[0] as f32 / resolution_max as f32, resolution[1] as f32 / resolution_max as f32];
  let axis_x = Array1::linspace(0.5 - 0.5 * axis_range[0], 0.5 + 0.5 * axis_range[0], resolution[0] + 1);
  let axis_y = Array1::linspace(0.5 - 0.5 * axis_range[1], 0.5 + 0.5 * axis_range[1], resolution[1] + 1);
  let ret_r = extrinsic_inv * na::Vector4::new(0., 0., 0., 1.);
  let mut ray_corner = Array3::zeros((6, resolution[1] + 1, resolution[0] + 1));
  ray_corner.axis_iter_mut(Axis(2)).enumerate().for_each(|(x, mut ray_corner)| {
    ray_corner.axis_iter_mut(Axis(1)).enumerate().for_each(|(y, mut ray_corner)| {
      let axis_xyz = intrinsic_inv * na::Vector3::new(axis_x[x], axis_y[y], 1.);
      let ret_rd = extrinsic_inv * na::Vector4::new(axis_xyz[0], axis_xyz[1], axis_xyz[2], 0.);
      for i in 0..3 {
        ray_corner[i] = ret_r[i];
        ray_corner[i + 3] = ret_rd[i];
      }
    });
  });
  from_ray_corner(ray_corner)
}

/// Python version [`perspective_ray`]
#[pyfunction]
#[pyo3(name = "perspective_ray")]
pub fn py_perspective_ray<'py>(
    py: Python<'py>,
    resolution: [usize; 2],
    intrinsic: PyReadonlyArray2<f32>,
    extrinsic: PyReadonlyArray2<f32>) -> Result<Bound<'py, PyArray3<f32>>> {
  ensure!(intrinsic.shape() == [3, 3],
    "camera::perspective_ray: `intrinsic` expected shape {:?}, found {:?}", [3, 3], intrinsic.shape());
  let intrinsic = intrinsic.try_as_matrix().expect("nalgebra dynamic stride");
  ensure!(extrinsic.shape() == [4, 4],
    "camera::perspective_ray: `extrinsic` expected shape {:?}, found {:?}", [4, 4], extrinsic.shape());
  let extrinsic = extrinsic.try_as_matrix().expect("nalgebra dynamic stride");
  let ray = perspective_ray(&resolution, intrinsic, extrinsic)?;
  Ok(ray.into_pyarray(py))
}
