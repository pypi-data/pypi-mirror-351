use std::path::Path;
use std::collections::HashSet;
use chrono::Utc;
use tracing::info;
use blake3::Hasher;
use nalgebra as na;
use anyhow::{Result, ensure, bail};
use serde::{Deserialize, Serialize};
use ndarray::{prelude::*, Slice, concatenate};
use tobj::{load_obj, GPU_LOAD_OPTIONS};
use super::message::*;

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
struct TriMesh {
  /// 4 * 4 homogeneous transformation matrix for vertex coordinate
  transform_v: Array2<f32>,
  /// 3 * 3 homogeneous transformation matrix for vertex texture coordinate
  transform_vt: Array2<f32>,
  /// Hash of TriMeshData
  trimesh_data: Hash,
}

fn area_cross(uv_a: na::Vector2<f32>, uv_b: na::Vector2<f32>, uv_o: na::Vector2<f32>) -> f32 {
	(uv_a[0] - uv_o[0]) * (uv_b[1] - uv_o[1]) - (uv_a[1] - uv_o[1]) * (uv_b[0] - uv_o[0])
}

fn dist_dot(uv_a: na::Vector2<f32>, uv_o: na::Vector2<f32>) -> f32 {
	f32::sqrt((uv_a - uv_o).dot(&(uv_a - uv_o)))
}

/// Generate a uv_xyz map from a combined geometry
///
/// xyz coordinate + padding distance
pub fn uv_xyz(vertex: ArrayView3<f32>, texture_resolution: usize, padding: usize) -> Result<Array3<f32>> {
  let size_geometry = vertex.shape()[2];
  assert_eq!(vertex.shape(), &[8, 3, size_geometry]);
  let mut xyz = Array3::zeros((4, texture_resolution, texture_resolution));
  xyz.index_axis_mut(Axis(0), 3).fill(padding as f32);
  for vertex in vertex.axis_iter(Axis(2)) {
    // 3 rows for 3 vertex
    let v_curr = na::Matrix3::<f32>::from_vec(vertex.slice_axis(Axis(0), Slice::from(0..3)).to_owned().into_raw_vec());
    let vt_curr = texture_resolution as f32 *
      na::Matrix3x2::<f32>::from_vec(vertex.slice_axis(Axis(0), Slice::from(6..8)).to_owned().into_raw_vec());
    // dbg!((v_curr, vt_curr));
    let area = area_cross(vt_curr.row(1).transpose(), vt_curr.row(2).transpose(), vt_curr.row(0).transpose());
    if f32::abs(area) < 1e-12 {
      continue;
    }
    let u_min = f32::max(0., vt_curr.column(0).min() - padding as f32) as usize;
    let u_max = f32::min(texture_resolution as f32, vt_curr.column(0).max() + padding as f32 + 1.) as usize;
    let v_min = f32::max(0., vt_curr.column(1).min() - padding as f32) as usize;
    let v_max = f32::min(texture_resolution as f32, vt_curr.column(1).max() + padding as f32 + 1.) as usize;
    for u in u_min..u_max {
      for v in v_min..v_max {
        let xyz_index = (texture_resolution - 1 - v, u);
        let center = na::Vector2::new(u as f32 + 0.5, v as f32 + 0.5);
        let area_0 = area_cross(center, vt_curr.row(2).transpose(), vt_curr.row(1).transpose());
        let dist_0 = area_0 / dist_dot(vt_curr.row(2).transpose(), vt_curr.row(1).transpose());
        let area_1 = area_cross(center, vt_curr.row(0).transpose(), vt_curr.row(2).transpose());
        let dist_1 = area_1 / dist_dot(vt_curr.row(0).transpose(), vt_curr.row(2).transpose());
        let area_2 = area_cross(center, vt_curr.row(1).transpose(), vt_curr.row(0).transpose());
        let dist_2 = area_2 / dist_dot(vt_curr.row(1).transpose(), vt_curr.row(0).transpose());
        let w = f32::max(1e-6, f32::min(1. - 1e-6, -area_2 / area));
        let v = f32::max(1e-6, f32::min(1. - 1e-6 - w, -area_1 / area));
        let u = 1. - 1e-6 - w - v;
        let dist_max = f32::max(dist_0, f32::max(dist_1, dist_2));
        let xyz_curr = v_curr.row(0) * u + v_curr.row(1) * v + v_curr.row(2) * w;
        if xyz[(3, xyz_index.0, xyz_index.1)] > dist_max {
          xyz[(0, xyz_index.0, xyz_index.1)] = xyz_curr[0];
          xyz[(1, xyz_index.0, xyz_index.1)] = xyz_curr[1];
          xyz[(2, xyz_index.0, xyz_index.1)] = xyz_curr[2];
          xyz[(3, xyz_index.0, xyz_index.1)] = dist_max;
        }
      }
    }
    // dbg!((u_min, u_max, v_min, v_max));
    // break;
  }
  // {
  //   use std::io::Write as _;
  //   let mut debug = std::fs::File::create("debug_xyz.bin")?;
  //   for val in xyz.iter() {
  //     debug.write_all(&val.to_le_bytes())?;
  //   }
  // }
  Ok(xyz)
}

/// Rust interface for Geometry
///
/// Trimeshes in scene geometry are lazy-loaded
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct Geometry {
  trimesh: Vec<TriMesh>,
}

impl Default for Geometry {
  fn default() -> Self {
    Geometry::new()
  }
}

impl Geometry {
  /// Construct an empty `Geometry`
  pub fn new() -> Self {
    Geometry {
      trimesh: Vec::new(),
    }
  }

  /// Number of all faces in `Geometry`
  pub fn size(&self, data_cache: &DataCache) -> Result<usize> {
    let mut size = 0;
    let data_cache = data_cache.lock().expect("No task should panic");
    for trimesh_data_hash in self.required_data() {
      data_cache.get(&trimesh_data_hash).map_or_else(|| {
        bail!("Geometry::size: Hash {trimesh_data_hash} not found");
      }, |entry| {
        let data = &entry.1;
        if let Data::TriMeshData(vertex) = data {
          size += vertex.shape()[2];
        } else {
          bail!("Geometry::size: Wrong data {trimesh_data_hash} {data}");
        }
        Ok(())
      })?;
    }
    Ok(size)
  }

  /// Calculate hash for lazy-loading
  ///
  /// Currently use 32-byte long hash from BLAKE3 algorithm.
  pub fn hash(&self) -> Hash {
    let mut hasher = Hasher::new();
    let msg = postcard::to_stdvec(self).expect("Internal Data Struct");
    hasher.update(&msg);
    Hash(*hasher.finalize().as_bytes())
  }

  /// Get all hashes of lazy-loading `Data`
  ///
  /// This includes all `v`, `vn`, and `vt`
  pub fn required_data(&self) -> HashSet<Hash> {
    HashSet::from_iter(self.trimesh.iter().map(|trimesh| trimesh.trimesh_data.to_owned()))
  }

  /// Add a trimesh to [`Geometry`] from hashed `vertex`
  ///
  /// # Arguments
  /// * `vertex_hash` - Vertex hash, generated from previous [`Self::add_trimesh`] or [`Self::add_obj`]
  /// * `transform_v` - Homogeneous transformation matrix for vertex coordinate 4 * 4
  /// * `transform_vt` - Homogeneous transformation matrix for vertex texture coordinate 3 * 3
  ///
  /// `vertex` is hashed and cached for better performance
  /// Return `vertex` hash for later use in `add_vertex_hash`
  pub fn add_vertex_hash (
      &mut self,
      vertex_hash: Hash,
      transform_v: Array2<f32>,
      transform_vt: Array2<f32>,
      data_cache: &DataCache) -> Result<Hash> {
    {
      let data_cache = data_cache.lock().expect("No task should panic");
      ensure!(data_cache.contains_key(&vertex_hash),
        "Geometry::add_vertex_hash: vertex hash {vertex_hash} doesn't exist in data_cache");
    }
    let trimesh = TriMesh {
      transform_v,
      transform_vt,
      trimesh_data: vertex_hash.to_owned(),
    };
    self.trimesh.push(trimesh);
    Ok(vertex_hash)
  }

  /// Add a trimesh to [`Geometry`]
  ///
  /// # Arguments
  /// * `vertex` - Vertex coordinate, normal, and texture coordinate (3 + 3 + 2) * 3 * N
  /// * `transform_v` - Homogeneous transformation matrix for vertex coordinate 4 * 4
  /// * `transform_vt` - Homogeneous transformation matrix for vertex texture coordinate 3 * 3
  ///
  /// `vertex` is hashed and cached for better performance
  /// Return `vertex` hash for later use in [`Self::add_vertex_hash`]
  pub fn add_trimesh(
      &mut self,
      vertex: Array3<f32>,
      transform_v: Array2<f32>,
      transform_vt: Array2<f32>,
      data_cache: &DataCache) -> Result<Hash> {
    let nf = vertex.shape()[2];
    ensure!(vertex.shape() == [8, 3, nf], "Geometry::add_trimesh: vertex.shape {:?}, expected {:?}",
      vertex.shape(), [8, 3, nf]);
    ensure!(transform_v.shape() == [4, 4], "Geometry::add_trimesh: transform_v.shape {:?}, expected {:?}",
      transform_v.shape(), [4, 4]);
    ensure!(transform_vt.shape() == [3, 3], "Geometry::add_trimesh: transform_vt.shape {:?}, expected {:?}",
      transform_vt.shape(), [3, 3]);
    let trimesh_data = Data::TriMeshData(vertex);
    let trimesh_data_hash = trimesh_data.hash();
    {
      let mut data_cache = data_cache.lock().expect("No task should panic");
      data_cache.insert(trimesh_data_hash.to_owned(), (Utc::now().timestamp(), trimesh_data));
    }
    self.add_vertex_hash(trimesh_data_hash, transform_v, transform_vt, data_cache)
  }

  /// Load Wavefront .obj trimesh to [`Geometry`]
  ///
  /// # Arguments
  /// * `filename` - Wavefront .obj file path
  /// * `transform_v` - Homogeneous transformation matrix for vertex coordinate 4 * 4
  /// * `transform_vt` - Homogeneous transformation matrix for vertex texture coordinate 3 * 3
  ///
  /// `vertex` is hashed and cached for better performance
  /// Return `vertex` hash for later use in `add_vertex_hash`
  pub fn add_obj(
      &mut self,
      filename: &Path,
      transform_v: Array2<f32>,
      transform_vt: Array2<f32>,
      data_cache: &DataCache) -> Result<Hash> {
    info!("Geometry::add_obj: loading {}", filename.display());
    let obj = load_obj(filename, &GPU_LOAD_OPTIONS)?.0;
    let mut vertex: Array3<f32> = Array3::default((8, 3, 0));
    for model in obj {
      let mesh = model.mesh;
      ensure!(!mesh.indices.is_empty(), "Geometry::add_obj: obj file {} is empty", filename.display());
      ensure!(!mesh.positions.is_empty(), "Geometry::add_obj: obj file {} is empty", filename.display());
      ensure!(!mesh.normals.is_empty(), "Geometry::add_obj: obj file {} has no vertex normal",
        filename.display());
      ensure!(!mesh.texcoords.is_empty(), "Geometry::add_obj: obj file {} has no texture coordinate",
        filename.display());
      // Number of faces
      let nf = mesh.indices.len() / 3;
      // Number of vertices
      let nv = mesh.positions.len() / 3;
      let mesh_indices = Array::from_shape_vec((nf, 3), mesh.indices)?;
      let mesh_positions = Array::from_shape_vec((nv, 3), mesh.positions)?;
      let mesh_normals = Array::from_shape_vec((nv, 3), mesh.normals)?;
      let mesh_texcoords = Array::from_shape_vec((nv, 2), mesh.texcoords)?;
      for indices in mesh_indices.axis_iter(Axis(0)) {
        let mut curr_vertex: Array2<f32> = Array2::default((8, 0));
        for j in 0..3 {
          // Don't transform now for better data cache
          curr_vertex.push(Axis(1), concatenate![Axis(0),
            mesh_positions.row(indices[j] as usize),
            mesh_normals.row(indices[j] as usize),
            mesh_texcoords.row(indices[j] as usize)].view())?;
        }
        vertex.push(Axis(2), curr_vertex.view())?;
      }
    }
    self.add_trimesh(vertex, transform_v, transform_vt, data_cache)
  }

  /// Apply transform and combine all trimeshes
  pub fn combine(&self, data_cache: &DataCache) -> Result<Array3<f32>> {
    let curr_timestamp = Utc::now().timestamp();
    let mut vertex: Array3<f32> = Array3::default((8, 3, 0));
    for trimesh in &self.trimesh {
      let mut data_cache = data_cache.lock().expect("No task should panic");
      let trimesh_data = data_cache.get_mut(&trimesh.trimesh_data).map_or_else(|| {
        bail!("Geometry::combine: Hash {} not found", trimesh.trimesh_data)
      }, |trimesh_data| {
        trimesh_data.0 = curr_timestamp;
        if let Data::TriMeshData(trimesh_data) = &trimesh_data.1 {
          Ok(trimesh_data)
        } else {
          bail!("Geometry::combine: Wrong data for `trimesh`: {}", &trimesh_data.1);
        }
      })?;
      let nf = trimesh_data.shape()[2];
      ensure!(trimesh_data.shape() == [8, 3, nf],
        "Geometry::combine: Wrong data shape {:?}, expected {:?}",
        trimesh_data.shape(), [8, 3, nf]);
      let mut v = trimesh_data.slice(s![..3, .., ..]).to_owned().into_shape([3, 3 * nf])?;
      v.push(Axis(0), Array1::ones(3 * nf).view())?;
      let v = trimesh.transform_v.dot(&v).slice(s![..3, ..]).to_owned().into_shape([3, 3, nf])?;
      let vn = trimesh_data.slice(s![3..6, .., ..]).to_owned().into_shape([3, 3 * nf])?;
      let vn = trimesh.transform_v.slice(s![..3, ..3]).dot(&vn).into_shape([3, 3, nf])?;
      let mut vt = trimesh_data.slice(s![6..8, .., ..]).to_owned().into_shape([2, 3 * nf])?;
      vt.push(Axis(0), Array1::ones(3 * nf).view())?;
      let vt = trimesh.transform_vt.dot(&vt).slice(s![..2, ..]).to_owned().into_shape([2, 3, nf])?;
      vertex.append(Axis(2), concatenate![Axis(0), v, vn, vt].view())?;
    }
    Ok(vertex)
  }

  /// Calculate uv_xyz of the combined geometry and cache the result
  pub fn uv_xyz_cached(&self, texture_resolution: usize, padding: usize, data_cache: &DataCache) -> Result<Array3<f32>> {
    let mut hasher = Hasher::new();
    let msg = postcard::to_stdvec(&(&self, texture_resolution, padding)).expect("Internal Data Struct");
    hasher.update(&msg);
    let hash = Hash(*hasher.finalize().as_bytes());
    {
      let mut data_cache = data_cache.lock().expect("No task should panic");
      if let Some(data) = data_cache.get_mut(&hash) {
        data.0 = Utc::now().timestamp();
        if let Data::TriMeshUVXYZ(uv_xyz) = &data.1 {
          return Ok(uv_xyz.to_owned());
        } else {
          bail!("Geometry::uv_xyz_cached: Wrong data for `uv_xyz`: {}", &data.1);
        }
      }
    }
    let vertex = self.combine(data_cache)?.as_standard_layout().into_owned();
    let uv_xyz = uv_xyz(vertex.view(), texture_resolution, padding)?;
    {
      let mut data_cache = data_cache.lock().expect("No task should panic");
      data_cache.insert(hash, (Utc::now().timestamp(), Data::TriMeshUVXYZ(uv_xyz.to_owned())));
    }
    Ok(uv_xyz)
  }
}
