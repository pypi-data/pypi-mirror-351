use nalgebra as na;
use ndarray::{Axis, Array4};
use anyhow::{Result, ensure};

/// Construct envmap with a given function
/// # Arguments
/// * `resolution`: a single integer
/// * `f`: function converting the normalized envmap direction (f32 vector of 3) to intensity (f32 vector of 3)
/// # Return
/// * 3 * 6 * `resolution` * `resolution`
pub fn functional_envmap<F>(resolution: usize, mut f: F) -> Result<Array4<f32>>
    where F: FnMut(na::Vector3<f32>) -> na::Vector3<f32> {
  let mut envmap = Array4::zeros((3, 6, resolution, resolution));
  for (face_id, mut envmap) in envmap.axis_iter_mut(Axis(1)).enumerate() {
    for (i_row, mut envmap) in envmap.axis_iter_mut(Axis(1)).enumerate() {
      for (i_col, mut envmap) in envmap.axis_iter_mut(Axis(1)).enumerate() {
        let i_row = ((resolution - 1 - i_row) as f32 + 0.5) / resolution as f32 * 2. - 1.;
        let i_col = (i_col as f32 + 0.5) / resolution as f32 * 2. - 1.;
        let mut axis_xyz = na::Vector3::zeros();
        axis_xyz[face_id / 2] = if face_id % 2 == 0 { 1. } else { -1. };
        match face_id / 2 {
          0 => (axis_xyz[2], axis_xyz[1]) = (i_row, i_col),
          1 => (axis_xyz[2], axis_xyz[0]) = (i_row, i_col),
          2 => (axis_xyz[1], axis_xyz[0]) = (i_row, i_col),
          _ => unreachable!(),
        }
        let intensity = f(axis_xyz.normalize());
        for (intensity, envmap) in intensity.into_iter().zip(envmap.iter_mut()) {
          ensure!(*intensity >= 0.,
                  "light_source::functional_envmap: negative `intensity` at {face_id} {i_row} {i_col}");
          ensure!(intensity.is_finite(),
                  "light_source::functional_envmap: infinite nor NaN `intensity` at {face_id} {i_row} {i_col}");
          *envmap = *intensity;
        }
      }
    }
  }
  Ok(envmap)
}
