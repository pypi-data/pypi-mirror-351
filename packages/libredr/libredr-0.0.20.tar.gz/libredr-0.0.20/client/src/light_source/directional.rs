use nalgebra as na;
use pyo3::prelude::*;
use ndarray::{s, Array4};
use anyhow::{Result, anyhow, ensure};
use numpy::{PyReadonlyArray1, PyArray4, IntoPyArray, PyUntypedArrayMethods};

const EPS: f32 = 1e-6;

/// Construct one-hot envmap with given direction and intensity
/// # Arguments
/// * `resolution`: a single integer
/// * `direction`: f32 vector of 3
/// * `intensity`: f32 scalar
/// # Return
/// * 3 * 6 * `resolution` * `resolution`
pub fn directional_envmap(resolution: usize, direction: na::VectorView3<f32>, intensity: f32) -> Result<Array4<f32>> {
  ensure!(direction.fold(true, |acc, v| { acc && v.is_finite() }),
          "light_source::directional_envmap: `direction` is not finite");
  let (face_id, abs_direction_max) = direction.abs().argmax();
  let direction = direction / abs_direction_max;
  let mut uv = match face_id {
    0 => [direction[1], direction[2]],
    1 => [direction[0], direction[2]],
    2 => [direction[0], direction[1]],
    _ => unreachable!(),
  };
  uv.iter_mut().for_each(|uv| {
    *uv = ((*uv + 1.) / 2.).clamp(EPS, 1. - EPS);
  });
  let envmap_col = (uv[0] * resolution as f32).floor() as usize;
  let envmap_row = resolution - 1 - (uv[1] * resolution as f32).floor() as usize;
  let face_id = face_id * 2 + (direction[face_id] < 0.) as usize;
  let intensity = intensity * (resolution as f32).powi(2) * direction.norm().powi(3);
  let mut envmap = Array4::zeros((3, 6, resolution, resolution));
  envmap.slice_mut(s![.., face_id, envmap_row, envmap_col]).fill(intensity);
  Ok(envmap)
}

/// Python version [`directional_envmap`]
#[pyfunction]
#[pyo3(name = "directional_envmap")]
pub fn py_directional_envmap<'py>(
    py: Python<'py>,
    resolution: usize,
    direction: PyReadonlyArray1<f32>,
    intensity: f32) -> Result<Bound<'py, PyArray4<f32>>> {
  let direction = direction.try_as_matrix().ok_or(
    anyhow!("light_source::directional_envmap: `direction` expected shape {:?}, found {:?}", [3], direction.shape()))?;
  let envmap = directional_envmap(resolution, direction, intensity)?;
  Ok(envmap.into_pyarray(py))
}
