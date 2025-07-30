use std::sync::{Arc, Mutex};
use std::collections::HashSet;
use uuid::Uuid;
use chrono::Utc;
use tracing::info;
use blake3::Hasher;
use ndarray::prelude::*;
use anyhow::{Result, bail, anyhow, ensure};
use serde::{Deserialize, Serialize};
use super::geometry::Geometry;
use super::connection::Connection;

/// Hash type for lazy-loading
///
/// Currently use 32-byte long hash from BLAKE3 algorithm.
#[derive(Serialize, Deserialize, Clone, Eq, Hash, PartialEq, Default)]
pub struct Hash(pub [u8; 32]);

impl std::fmt::Display for Hash {
  fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    write!(f, "[{:02X} {:02X} {:02X} {:02X}]", self.0[0], self.0[1], self.0[2], self.0[3])
  }
}

impl std::fmt::Debug for Hash {
  fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    write!(f, "{:?}", self.0)
  }
}

impl From<Uuid> for Hash {
  fn from(uuid: Uuid) -> Self {
    let mut ret = [0; 32];
    ret[..16].copy_from_slice(&uuid.into_bytes());
    Hash(ret)
  }
}

impl From<(&Uuid, &Uuid)> for Hash {
  fn from(uuid: (&Uuid, &Uuid)) -> Self {
    let mut ret = [0; 32];
    ret[..16].copy_from_slice(&uuid.0.into_bytes());
    ret[16..].copy_from_slice(&uuid.1.into_bytes());
    Hash(ret)
  }
}

impl From<u64> for Hash {
  fn from(hash: u64) -> Self {
    let mut ret = [0; 32];
    ret[..8].copy_from_slice(&hash.to_le_bytes());
    Hash(ret)
  }
}

/// Type for lazy-loading data cache
///
/// hash -> (access time, data)
pub type DataCache = Arc<Mutex<hashbrown::HashMap<Hash, (i64, Data)>>>;

/// All kinds of lazy-loading data types
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub enum Data {
  /// Vertex coordinate, vertex normal, and vertex texture coordinate of a TriMesh
  ///
  /// (3 + 3 + 2) * 3 * Number of faces
  TriMeshData(Array3<f32>),
  /// Ray tracing `ray`, see `ray` argument in `py_ray_tracing_forward`
  RayData(Array2<f32>),
  /// `texture` and `envmap`
  MaterialData(Array3<f32>, Array4<f32>),
  /// Cache for uv_xyz calculation, only on worker
  TriMeshUVXYZ(Array3<f32>),
  /// Cache intermediate data for back propagation and cumulate gradient to reduce communication, only on worker
  Intermediate(Intermediate),
}

/// Cache intermediate data for back propagation and cumulate gradient to reduce communication, only on worker
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct Intermediate {
  /// Uuid of the client task
  pub client_uuid: Uuid,
  /// Uuids of all the request tasks that are assigned to this worker \
  /// Save forward task and intermediate data for backward task
  pub forward_requests: hashbrown::HashMap<Uuid, (RequestRayTracingForward, Vec<u8>)>,
  /// Cumulate `d_texture` and only return to server on the last tile
  pub d_texture: Array3<f32>,
  /// Cumulate `d_envmap` and only return to server on the last tile
  pub d_envmap: Array4<f32>,
}

impl std::fmt::Display for Data {
  fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    match self {
      Data::TriMeshData(data) => write!(f, "Data::TriMeshData size: {}", data.shape()[2]),
      Data::RayData(data) => write!(f, "Data::RayData size: {}", data.shape()[1]),
      Data::MaterialData(texture, envmap) =>
        write!(f, "Data::MaterialData size: {:?} {:?}", texture.shape(), envmap.shape()),
      Data::TriMeshUVXYZ(data) => write!(f, "Data::TriMeshUVXYZ size: {}", data.shape()[1]),
      Data::Intermediate(intermediate) => write!(f, "Data::Intermediate client_uuid: {}", intermediate.client_uuid),
    }
  }
}

impl Data {
  /// Calculate hash for lazy-loading
  ///
  /// Currently use 32-byte long hash from BLAKE3 algorithm.
  pub fn hash(&self) -> Hash {
    let mut hasher = Hasher::new();
    let msg = postcard::to_stdvec(self).expect("Internal Data Struct");
    hasher.update(&msg);
    Hash(*hasher.finalize().as_bytes())
  }
}

/// Load all lazy-loading data hash from `required_data` into `data_cache`
///
/// The `Data` is fetched from `connection` \
/// All `Data` timestamps in `data_cache` are updated
pub async fn ensure_data(
    connection: &mut Connection,
    data_cache: &DataCache,
    mut required_data: HashSet<Hash>) -> Result<()> {
  {
    let mut data_cache = data_cache.lock().expect("No task should panic");
    required_data.retain(|data_hash| {
      data_cache.get_mut(data_hash).map_or_else(|| { true }, |entry| {
        entry.0 = Utc::now().timestamp();
        false
      })
    });
  }
  for data_hash in required_data.iter() {
    let request_task = Message::RequestData(data_hash.to_owned());
    info!("Message::ensure_data: {} Request {request_task}", connection.description());
    connection.send_msg(&request_task).await?
  }
  while !required_data.is_empty() {
    let msg_response = connection.recv_msg().await?;
    info!("Message::ensure_data: {} Response {msg_response}", connection.description());
    let Message::ResponseData(data) = msg_response else {
      bail!("ensure_data: Unexpected command from `{}`", connection.description());
    };
    let data = data.map_err(|err| {
      anyhow!("ensure_data: Remote reports `ResponseData` error: {err}")
    })?;
    let data_hash = data.hash();
    if required_data.remove(&data_hash) {
      let mut data_cache = data_cache.lock().expect("No task should panic");
      data_cache.insert(data_hash, (Utc::now().timestamp(), data));
    } else {
      bail!("ensure_data: Unexpected `ResponseData` hash {data_hash} from `{}`", connection.description());
    }
  }
  Ok(())
}

/// Get `hash` data from `data_cache`, return result of f(data)
///
/// To prevent data copy, `data` is not returned
pub fn map_cache_data<R, F>(hash: &Hash, data_cache: &DataCache, f: F) -> Result<R>
    where F: FnOnce(&Data) -> Result<R> {
  let mut data_cache = data_cache.lock().expect("No task should panic");
  let data = data_cache.get_mut(hash).ok_or_else(||
    anyhow!("Message: map_cache_data: Hash {hash} not found"))?;
  data.0 = Utc::now().timestamp();
  f(&data.1)
}

/// Get `hash` data from `data_cache`, insert result of f(data), return new hash
pub fn insert_map_cache_data<F>(hash: &Hash, data_cache: &DataCache, f: F) -> Result<Hash>
    where F: FnOnce(&Data) -> Result<Data> {
  let mut data_cache = data_cache.lock().expect("No task should panic");
  let data = data_cache.get_mut(hash).ok_or_else(|| anyhow!("Message: map_cache_data: Hash {hash} not found"))?;
  data.0 = Utc::now().timestamp();
  let new_data = f(&data.1)?;
  let new_data_hash = new_data.hash();
  data_cache.insert(new_data_hash.to_owned(), (Utc::now().timestamp(), new_data));
  Ok(new_data_hash)
}

/// Arguments for ray-tracing forward task
///
/// See arguments in `ray_tracing_forward` for details
#[allow(missing_docs)]
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct RequestRayTracingForward {
  /// Lazy-loading `geometry`
  pub geometry: Geometry,
  /// Lazy-loading `ray`
  pub ray: Hash,
  /// Lazy-loading `texture` and `envmap`
  pub material: Hash,
  pub sample_per_pixel: (usize, usize),
  pub max_bounce: (usize, usize, usize, usize),
  pub switches: (u8, u8, u8, u8),
  pub clip_near: (f32, f32, f32),
  pub camera_space: bool,
  pub requires_grad: bool,
  pub srand: i32,
  pub low_discrepancy: u32,
}

impl RequestRayTracingForward {
  /// Number of rays in [`RequestRayTracingForward`]
  pub fn size(&self, data_cache: &DataCache) -> Result<usize> {
    map_cache_data(&self.ray, data_cache, |ray| {
      if let Data::RayData(ray) = ray {
        Ok(ray.shape()[1])
      } else {
        bail!("RequestRayTracingForward::size: Wrong data for argument `ray`: {ray}");
      }
    })
  }

  /// Texture resolution and envmap resolution in [`RequestRayTracingForward`]
  pub fn material_resolution(&self, data_cache: &DataCache) -> Result<(usize, usize)> {
    map_cache_data(&self.material, data_cache, |material| {
      if let Data::MaterialData(texture, envmap) = material {
        Ok((texture.shape()[2], envmap.shape()[3]))
      } else {
        bail!("RequestRayTracingForward::material_resolution: Wrong data for argument `material`: {material}");
      }
    })
  }
}

// Because we hardly see same parameter cross different backward tasks, we don't lazy-load backward data
#[allow(missing_docs)]
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct RequestRayTracingBackward {
  /// `d_ray`, must have the same number of rays as [`RequestRayTracingForward`]
  pub d_ray: Array2<f32>,
}

impl RequestRayTracingBackward {
  /// Number of rays in `RequestRayTracingBackward`
  pub fn size(&self, _data_cache: &DataCache) -> Result<usize> {
    Ok(self.d_ray.shape()[1])
  }
}

#[allow(missing_docs)]
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub enum RequestTask {
  // Boxed because of large size difference
  RequestRayTracingForward(Box<RequestRayTracingForward>),
  RequestRayTracingBackward(Box<RequestRayTracingBackward>),
}

impl std::fmt::Display for RequestTask {
  fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    match self {
      RequestTask::RequestRayTracingForward(request) =>
        write!(f, "RequestTask::RequestRayTracingForward requires_grad: {}", request.requires_grad),
      RequestTask::RequestRayTracingBackward(_) => write!(f, "RequestTask::RequestRayTracingBackward"),
    }
  }
}

/// Functions to split task into multiple sub-tasks for worker
impl RequestTask {
  /// Get task size for split
  pub fn size(&self, data_cache: &DataCache) -> Result<usize> {
    match self {
      RequestTask::RequestRayTracingForward(request) => request.size(data_cache),
      RequestTask::RequestRayTracingBackward(request) => request.size(data_cache),
    }
  }

  /// Generate a sub-task by slicing current task from `progress` to `progress + tile_size`
  ///
  /// The last piece can be smaller than `tile_size` \
  /// `progress` is updated automatically
  pub fn split(&self, progress: &mut usize, tile_size: usize, data_cache: &DataCache) -> Result<Option<Self>> {
    let new_progress = std::cmp::min(*progress + tile_size, self.size(data_cache)?);
    if *progress >= new_progress {
      Ok(None)
    } else {
      let sub_task = Some(match self {
        RequestTask::RequestRayTracingForward(request) =>
          RequestTask::RequestRayTracingForward(Box::new({
            let sub_ray_hash = insert_map_cache_data(&request.ray, data_cache, |ray| {
              if let Data::RayData(ray) = ray {
                Ok(Data::RayData(ray.slice(s![.., *progress..new_progress]).to_owned()))
              } else {
                bail!("Message::RequestTask::size: Wrong data for argument `ray`: {ray}");
              }
            })?;
            RequestRayTracingForward {
              geometry: request.geometry.to_owned(),
              ray: sub_ray_hash,
              material: request.material.to_owned(),
              ..**request
            }
          })),
        RequestTask::RequestRayTracingBackward(request) =>
          RequestTask::RequestRayTracingBackward(Box::new({
            let sub_d_ray = request.d_ray.slice(s![.., *progress..new_progress]).to_owned();
            RequestRayTracingBackward {
              d_ray: sub_d_ray,
            }
          })),
      });
      *progress = new_progress;
      Ok(sub_task)
    }
  }

  /// Get all hashes of lazy-loading `Data`
  pub fn required_data(&self) -> HashSet<Hash> {
    match self {
      RequestTask::RequestRayTracingForward(request) => {
        let mut ret = HashSet::new();
        ret.extend(request.geometry.required_data());
        ret.insert(request.ray.to_owned());
        ret.insert(request.material.to_owned());
        ret
      },
      RequestTask::RequestRayTracingBackward(_request) => HashSet::new(),
    }
  }

  /// Create an empty `ResponseTask` as the same type of `RequestTask`
  pub fn new_response(&self) -> ResponseTask {
    match self {
      RequestTask::RequestRayTracingForward(request) => ResponseTask::ResponseRayTracingForward(
        Box::new(ResponseRayTracingForward {
          // * if `camera_space` is `true`, (3)
          //   * ray_render
          // * if `camera_space` is `false`, (3 + 2 + 1 + 3)
          //   * ray_render + ray_texture + ray_depth + ray_normal
          render: Array2::default((if request.camera_space { 3 } else { 9 }, 0)),
        })
      ),
      RequestTask::RequestRayTracingBackward(_) => ResponseTask::ResponseRayTracingBackward(
        Box::new(ResponseRayTracingBackward {
          d_texture: None,
          d_envmap: None,
          d_ray_texture: None,
        })
      ),
    }
  }
}

#[allow(missing_docs)]
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct ResponseRayTracingForward {
  pub render: Array2<f32>,
}

impl ResponseRayTracingForward {
  fn merge(&mut self, other: &ResponseRayTracingForward) -> Result<()> {
    self.render.append(Axis(1), other.render.view())?;
    Ok(())
  }
}

#[allow(missing_docs)]
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct ResponseRayTracingBackward {
  pub d_texture: Option<Array3<f32>>,
  pub d_envmap: Option<Array4<f32>>,
  pub d_ray_texture: Option<Array2<f32>>,
}

impl ResponseRayTracingBackward {
  fn merge(&mut self, other: &ResponseRayTracingBackward) -> Result<()> {
    ensure!(other.d_texture.is_some() == other.d_texture.is_some());
    if let Some(d_texture) = &mut self.d_texture {
      if let Some(other_d_texture) = &other.d_texture {
        ensure!(d_texture.shape() == other_d_texture.shape(), "ResponseRayTracingBackward::merge:
          d_texture shape mismatch {:?} and {:?}", d_texture.shape(), other_d_texture.shape());
        *d_texture += other_d_texture;
      }
    } else {
      self.d_texture = other.d_texture.to_owned();
    }
    if let Some(d_envmap) = &mut self.d_envmap {
      if let Some(other_d_envmap) = &other.d_envmap {
        ensure!(d_envmap.shape() == other_d_envmap.shape(), "ResponseRayTracingBackward::merge:
        d_envmap shape mismatch {:?} and {:?}", d_envmap.shape(), other_d_envmap.shape());
        *d_envmap += other_d_envmap;
      }
    } else {
      self.d_envmap = other.d_envmap.to_owned();
    }
    if let Some(other_d_ray_texture) = &other.d_ray_texture {
      if let Some(d_ray_texture) = &mut self.d_ray_texture {
        d_ray_texture.append(Axis(1), other_d_ray_texture.view())?;
      } else {
        self.d_ray_texture = Some(other_d_ray_texture.to_owned());
      }
    }
    Ok(())
  }
}

#[allow(missing_docs)]
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub enum ResponseTask {
  ResponseRayTracingForward(Box<ResponseRayTracingForward>),
  ResponseRayTracingBackward(Box<ResponseRayTracingBackward>),
}

impl std::fmt::Display for ResponseTask {
  fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    match self {
      ResponseTask::ResponseRayTracingForward(_) => write!(f, "ResponseTask::ResponseRayTracingForward"),
      ResponseTask::ResponseRayTracingBackward(_) => write!(f, "ResponseTask::ResponseRayTracingBackward"),
    }
  }
}

#[allow(missing_docs)]
impl ResponseTask {
  pub fn merge(&mut self, other: &ResponseTask) -> Result<()> {
    match self {
      ResponseTask::ResponseRayTracingForward(response_task) => {
        let ResponseTask::ResponseRayTracingForward(other) = other else {
          bail!("ResponseTask::merge ResponseRayTracingForward and {other}");
        };
        response_task.merge(other)
      },
      ResponseTask::ResponseRayTracingBackward(response_task) => {
        let ResponseTask::ResponseRayTracingBackward(other) = other else {
          bail!("ResponseTask::merge ResponseRayTracingBackward and {other}");
        };
        response_task.merge(other)
      },
    }
  }
}

/// Pair of `client_uuid` and `request_uuid` to help worker find and merge intermediate data
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct GradUUID {
  #[allow(missing_docs)]
  pub client_uuid: Uuid,
  #[allow(missing_docs)]
  pub request_uuid: Uuid,
}

impl GradUUID {
  /// Create `GradUUID` with both `client_uuid` and `request_uuid` as nil
  pub fn nil() -> Self {
    GradUUID { client_uuid: Uuid::nil(), request_uuid: Uuid::nil() }
  }

  /// Test if `GradUUID` is nil
  pub fn is_nil(&self) -> bool {
    self.client_uuid.is_nil() && self.request_uuid.is_nil()
  }
}

/// `Message` type shared by Client, Server, and Worker
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub enum Message {
  /// Check remote version
  Version(String, String, String),
  /// Request lazy-loading data by hash
  RequestData(Hash),
  /// Response lazy-loading data
  ///
  /// Error if the data-cache is cleaned up
  ResponseData(Box<Result<Data, String>>),
  /// Notify the worker `GradUUID` to save and merge intermediate data
  RequestGradUUID(GradUUID),
  /// All types of `RequestTask`
  RequestTask(RequestTask),
  /// All types of `ResponseTask`
  ResponseTask(Result<ResponseTask, String>),
  /// Close cleanly
  Close(),
}

impl std::fmt::Display for Message {
  fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    match self {
      Message::Version(ver, git, build) => write!(f, "Message::Version {ver} - {git} - {build}"),
      Message::RequestData(msg) => write!(f, "Message::RequestData {msg}"),
      Message::ResponseData(msg) => match msg.as_ref() {
        Ok(msg) => write!(f, "Message::ResponseData {msg}"),
        Err(err) => write!(f, "Message::ResponseData Error {err}"),
      },
      Message::RequestGradUUID(_) => write!(f, "Message::RequestGradUUID"),
      Message::RequestTask(msg) => write!(f, "Message::RequestTask {msg}"),
      Message::ResponseTask(msg) => match msg {
        Ok(msg) => write!(f, "Message::ResponseTask {msg}"),
        Err(err) => write!(f, "Message::ResponseTask Error {err}"),
      },
      Message::Close() => write!(f, "Message::Close"),
    }
  }
}
