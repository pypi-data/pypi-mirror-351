#![doc = include_str!("../README.md")]
#![warn(missing_docs)]
#![warn(missing_debug_implementations)]

use std::env;
use std::path::Path;
use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use anyhow::{Result, bail};
use tokio::runtime::Runtime;
use tracing::{error, debug};
use once_cell::sync::OnceCell;
use tracing_subscriber::{fmt, EnvFilter, prelude::*};
use numpy::{PyReadonlyArray2, PyReadonlyArray3, PyReadonlyArray4, PyReadonlyArrayDyn, PyArray3, PyArray4, PyArrayDyn,
  IntoPyArray, PyArrayMethods};
use common::render;
use common::message::*;
pub use common::geometry::Geometry;
pub use self::client::LibreDR;
use self::camera::py_camera;
use self::light_source::py_light_source;

mod client;
/// All camera models (Rust and Python)
pub mod camera;
/// All light source models (Rust and Python)
pub mod light_source;

static RUNTIME: OnceCell<Runtime> = OnceCell::new();

/// Python interface for [`Geometry`]
#[derive(Debug)]
#[pyclass(name = "Geometry", subclass)]
pub struct PyGeometry {
  geometry: Geometry,
  data_cache: DataCache,
}

/// Python interface for [`LibreDR`] client
#[derive(Debug)]
#[pyclass(name = "LibreDR", subclass)]
pub struct PyLibreDR(LibreDR, String, bool, bool);

#[pymethods]
impl PyGeometry {
  #[new]
  /// Create an empty [`PyGeometry`]
  pub fn py_new() -> Self {
    PyGeometry {
      geometry: Geometry::new(),
      data_cache: Arc::new(Mutex::new(hashbrown::HashMap::new())),
    }
  }

  // TODO: add_trimesh (using vertex and face arrays from python)
  /// See [`Geometry::add_obj`]
  #[pyo3(name = "add_obj")]
  pub fn py_add_obj(
      &mut self,
      py: Python,
      filename: &str,
      transform_v: PyReadonlyArray2<f32>,
      transform_vt: PyReadonlyArray2<f32>) -> Result<()> {
    let transform_v = transform_v.to_owned_array();
    let transform_vt = transform_vt.to_owned_array();
    py.allow_threads(|| {
      self.geometry.add_obj(Path::new(filename), transform_v, transform_vt, &self.data_cache)
    })?;
    Ok(())
  }
}

#[pymethods]
impl PyLibreDR {
  /// See [`render::MISS_NONE`] for details.
  #[classattr]
  pub const MISS_NONE: u8 = render::MISS_NONE;
  /// See [`render::MISS_ENVMAP`] for details.
  #[classattr]
  pub const MISS_ENVMAP: u8 = render::MISS_ENVMAP;
  /// See [`render::REFLECTION_NORMAL_FACE`] for details.
  #[classattr]
  pub const REFLECTION_NORMAL_FACE: u8 = render::REFLECTION_NORMAL_FACE;
  /// See [`render::REFLECTION_NORMAL_VERTEX`] for details.
  #[classattr]
  pub const REFLECTION_NORMAL_VERTEX: u8 = render::REFLECTION_NORMAL_VERTEX;
  /// See [`render::REFLECTION_NORMAL_TEXTURE`] for details.
  #[classattr]
  pub const REFLECTION_NORMAL_TEXTURE: u8 = render::REFLECTION_NORMAL_TEXTURE;
  /// See [`render::REFLECTION_DIFFUSE_NONE`] for details.
  #[classattr]
  pub const REFLECTION_DIFFUSE_NONE: u8 = render::REFLECTION_DIFFUSE_NONE;
  /// See [`render::REFLECTION_DIFFUSE_LAMBERTIAN`] for details.
  #[classattr]
  pub const REFLECTION_DIFFUSE_LAMBERTIAN: u8 = render::REFLECTION_DIFFUSE_LAMBERTIAN;
  /// See [`render::REFLECTION_SPECULAR_NONE`] for details.
  #[classattr]
  pub const REFLECTION_SPECULAR_NONE: u8 = render::REFLECTION_SPECULAR_NONE;
  /// See [`render::REFLECTION_SPECULAR_PHONG`] for details.
  #[classattr]
  pub const REFLECTION_SPECULAR_PHONG: u8 = render::REFLECTION_SPECULAR_PHONG;
  /// See [`render::REFLECTION_SPECULAR_BLINN_PHONG`] for details.
  #[classattr]
  pub const REFLECTION_SPECULAR_BLINN_PHONG: u8 = render::REFLECTION_SPECULAR_BLINN_PHONG;
  /// See [`render::REFLECTION_SPECULAR_TORRANCE_SPARROW_PHONG`] for details.
  #[classattr]
  pub const REFLECTION_SPECULAR_TORRANCE_SPARROW_PHONG: u8 = render::REFLECTION_SPECULAR_TORRANCE_SPARROW_PHONG;
  /// See [`render::REFLECTION_SPECULAR_TORRANCE_SPARROW_BLINN_PHONG`] for details.
  #[classattr]
  pub const REFLECTION_SPECULAR_TORRANCE_SPARROW_BLINN_PHONG: u8 =
    render::REFLECTION_SPECULAR_TORRANCE_SPARROW_BLINN_PHONG;
    /// See [`render::REFLECTION_SPECULAR_TORRANCE_SPARROW_BECKMANN`] for details.
  #[classattr]
  pub const REFLECTION_SPECULAR_TORRANCE_SPARROW_BECKMANN: u8 = render::REFLECTION_SPECULAR_TORRANCE_SPARROW_BECKMANN;

  /// Construct `LibreDR` by connecting to LibreDR server.
  ///
  /// See [`LibreDR::new`] for details.
  #[new]
  pub fn py_new(py: Python, connect: String, unix: bool, tls: bool) -> Result<Self> {
    let libredr = py.allow_threads(|| {
      let rt = RUNTIME.get().expect("Initialized in pymodule");
      rt.block_on(LibreDR::new(connect.to_owned(), unix, tls))
    })?;
    Ok(PyLibreDR(libredr, connect, unix, tls))
  }

  /// To allow pickle [`PyLibreDR`] object by reconnecting to the server.
  ///
  /// Unpickled connection has different UUID.
  pub fn __getnewargs__(&self) -> (String, bool, bool) {
    (self.1.to_owned(), self.2, self.3)
  }

  /// Create a [`RequestRayTracingForward`] task and wait for response
  ///
  /// # Arguments
  /// * `ray` - ray parameters
  ///   * if `camera_space` is `false` 18 * `image_shape`
  ///     * including ray position 9 * `image_shape`
  ///     * including ray direction 9 * `image_shape`
  ///   * if `camera_space` is `true`, add another (1 + 14) channels
  ///     * including ray depth 1 * `image_shape` (if depth <= 0, treat as hit miss)
  ///     * including ray material 14 * `image_shape`
  /// * `texture` - (3 + 3 + 3 + 1 + 3 + 1) * `texture_resolution` * `texture_resolution` (must be square image)
  ///   * including normal + diffuse + specular + roughness + intensity + window
  /// * `envmap` - 3 * 6 * `envmap_resolution` * `envmap_resolution`
  ///   * (must be box unwrapped 6 square images)
  /// * `sample_per_pixel` - `sample_per_pixel_forward`, (`sample_per_pixel_backward`)
  ///   * `sample_per_pixel` can be a single integer,
  ///     * (same value for forward and backward)
  ///   * or tuple of 2 integers.
  ///     * (only `sample_per_pixel_backward` number of rays are stored for backward)
  ///     * (must ensure `sample_per_pixel_forward` >= `sample_per_pixel_backward`)
  /// * `max_bounce` - `max_bounce_forward`, (`max_bounce_backward`), (`max_bounce_low_discrepancy`), (`skip_bounce`)
  ///   * `max_bounce` can be a single integer, or tuple of 2-4 integers.
  ///   * The default value for `max_bounce_backward` is the same as `max_bounce_forward`.
  ///   * The default value for `max_bounce_low_discrepancy` is `0`.
  ///   * The default value for `skip_bounce` is `0`.
  /// * `switches` - tuple of 4 switches to determine hit miss and reflection behavior
  ///   * render::MISS_* - determine how to deal with ray hit miss
  ///     * [`common::render::MISS_NONE`]
  ///     * [`common::render::MISS_ENVMAP`]
  ///   * render::REFLECTION_NORMAL_* - determine how to get surface normal
  ///     * [`common::render::REFLECTION_NORMAL_FACE`]
  ///     * [`common::render::REFLECTION_NORMAL_VERTEX`]
  ///     * [`common::render::REFLECTION_NORMAL_TEXTURE`]
  ///   * render::REFLECTION_DIFFUSE_* - determine diffuse reflection model
  ///     * [`common::render::REFLECTION_DIFFUSE_NONE`]
  ///     * [`common::render::REFLECTION_DIFFUSE_LAMBERTIAN`]
  ///   * render::REFLECTION_SPECULAR_* - determine specular reflection model
  ///     * [`common::render::REFLECTION_SPECULAR_NONE`]
  ///     * [`common::render::REFLECTION_SPECULAR_PHONG`]
  ///     * [`common::render::REFLECTION_SPECULAR_BLINN_PHONG`]
  ///     * [`common::render::REFLECTION_SPECULAR_TORRANCE_SPARROW_PHONG`]
  ///     * [`common::render::REFLECTION_SPECULAR_TORRANCE_SPARROW_BLINN_PHONG`]
  ///     * [`common::render::REFLECTION_SPECULAR_TORRANCE_SPARROW_BECKMANN`]
  /// * `clip_near` - clip near distance for camera
  ///   * `clip_near` can be a single float number (same for all bounces),
  ///   * or tuple of 3 float numbers (first bounce, second bounce, and other bounces)
  /// * `camera_space` - if `true`, the first bounce uses the depth and material given by the ray
  /// * `requires_grad` - if `true`, worker will save intermediate data, the next task must be `ray_tracing_backward`
  /// * `srand` - random seed
  ///   * if srand >= 0, the same random seed is used for every pixel
  ///   * if srand < 0, use different seed for each pixel
  /// * `low_discrepancy` - (optional) start id of Halton low discrepancy sequence.
  ///   * The default value is the same as `sample_per_pixel_forward`.
  ///   * if combine multiple rendered images to reduce noise, this value can be set to: \
  ///       1 * `sample_per_pixel_forward`, 2 * `sample_per_pixel_forward`, 3 * `sample_per_pixel_forward`, ...
  ///
  /// # Return
  /// Return shape will be,
  ///   * if `camera_space` is `true`
  ///     * render image 3 * `image_shape`
  ///   * if `camera_space` is `false`, add another
  ///     * ray texture coordinate 2 * `image_shape`
  ///     * ray depth (Euclidean distance) 1 * `image_shape`
  ///     * ray normal 3 * `image_shape`
  #[pyo3(name = "ray_tracing_forward")]
  #[allow(clippy::too_many_arguments)]
  pub fn py_ray_tracing_forward<'py>(
      &mut self,
      py: Python<'py>,
      geometry: &PyGeometry,
      ray: PyReadonlyArrayDyn<f32>,
      texture: PyReadonlyArray3<f32>,
      envmap: PyReadonlyArray4<f32>,
      sample_per_pixel: Py<PyAny>,
      max_bounce: Py<PyAny>,
      switches: (u8, u8, u8, u8),
      clip_near: Py<PyAny>,
      camera_space: bool,
      requires_grad: bool,
      srand: i32,
      low_discrepancy: Option<u32>) -> Result<Bound<'py, PyArrayDyn<f32>>> {
    debug!("py_ray_tracing_forward: enter");
    let ray = ray.to_owned_array();
    let texture = texture.to_owned_array();
    let envmap = envmap.to_owned_array();
    let sample_per_pixel:(usize, usize) = if let Ok(sample_per_pixel_forward) = sample_per_pixel.extract(py) {
      (sample_per_pixel_forward, sample_per_pixel_forward)
    } else if let Ok(sample_per_pixel) = sample_per_pixel.extract(py) {
      sample_per_pixel
    } else {
      bail!("py_ray_tracing_forward: invalid type in sample_per_pixel")
    };
    let max_bounce:(usize, usize, usize, usize) = if let Ok(max_bounce_forward) = max_bounce.extract(py) {
      (max_bounce_forward, max_bounce_forward, 0, 0)
    } else if let Ok((max_bounce_forward, max_bounce_backward)) = max_bounce.extract(py) {
      (max_bounce_forward, max_bounce_backward, 0, 0)
    } else if let Ok((max_bounce_forward, max_bounce_backward, max_bounce_low_discrepancy)) = max_bounce.extract(py) {
      (max_bounce_forward, max_bounce_backward, max_bounce_low_discrepancy, 0)
    } else if let Ok(max_bounce) = max_bounce.extract(py) {
      max_bounce
    } else {
      bail!("py_ray_tracing_forward: invalid type in max_bounce")
    };
    let clip_near:(f32, f32, f32) = if let Ok(clip_near) = clip_near.extract(py) {
      (clip_near, clip_near, clip_near)
    } else if let Ok(clip_near) = clip_near.extract(py) {
      clip_near
    } else {
      bail!("py_ray_tracing_forward: invalid type in clip_near")
    };
    let low_discrepancy = low_discrepancy.unwrap_or(sample_per_pixel.0.try_into()?);
    let response = py.allow_threads(|| {
      let rt = RUNTIME.get().expect("Initialized in pymodule");
      rt.block_on(self.0.ray_tracing_forward(
        &geometry.geometry,
        &geometry.data_cache,
        ray,
        texture,
        envmap,
        sample_per_pixel,
        max_bounce,
        switches,
        clip_near,
        camera_space,
        requires_grad,
        srand,
        low_discrepancy
      ))
    })?;
    Ok(response.into_pyarray(py))
  }

  /// Create a [`RequestRayTracingBackward`] task and wait for response.
  ///
  /// Must be called consecutive to a [`RequestRayTracingForward`] task with `requires_grad` set to `true`. \
  /// To create multiple [`RequestRayTracingForward`] tasks and backward together, multiple client connections are
  /// required.
  ///
  /// # Arguments
  /// * `d_ray` - gradient of image 3 * `image_shape` (must ensure same `image_shape` as [`RequestRayTracingForward`])
  ///
  /// # Return
  /// Return shape will be,
  /// * if `camera_space` is `false` for [`RequestRayTracingForward`] task
  ///   * 1st return value (3 + 3 + 3 + 1 + 3 + 1) * `texture_resolution` * `texture_resolution`
  ///     * (same `texture_resolution` as [`RequestRayTracingForward`])
  ///     * including d_normal + d_diffuse + d_specular + d_roughness + d_intensity + d_window
  ///   * 2nd return value 3 * 6 * `envmap_resolution` * `envmap_resolution`
  ///     * (same `envmap_resolution` as [`RequestRayTracingForward`])
  ///     * including d_envmap
  /// * if `camera_space` is `true` for [`RequestRayTracingForward`] task, add another
  ///   * 3rd return value 14 * `image_shape` (same shape as [`RequestRayTracingForward`])
  ///     * including d_ray_texture
  #[pyo3(name = "ray_tracing_backward")]
  #[allow(clippy::type_complexity)]
  pub fn py_ray_tracing_backward<'py>(
      &mut self,
      py: Python<'py>,
      d_ray: PyReadonlyArrayDyn<f32>
    ) -> Result<(Bound<'py, PyArray3<f32>>, Bound<'py, PyArray4<f32>>, Option<Bound<'py, PyArrayDyn<f32>>>)> {
    debug!("py_ray_tracing_backward: enter");
    let d_ray = d_ray.to_owned_array();
    let response = py.allow_threads(|| {
      let rt = RUNTIME.get().expect("Initialized in pymodule");
      rt.block_on(self.0.ray_tracing_backward(d_ray))
    })?;
    let d_texture = response.0.into_pyarray(py);
    let d_envmap = response.1.into_pyarray(py);
    let d_ray_texture = response.2.map(|d_ray_texture| d_ray_texture.into_pyarray(py));
    Ok((d_texture, d_envmap, d_ray_texture))
  }
}

impl Drop for PyLibreDR {
  fn drop(&mut self) {
    let rt = RUNTIME.get().expect("Initialized in pymodule");
    rt.block_on(async {
      if let Err(err) = self.0.close().await {
        error!("PyLibreDR::drop: {}", err);
      }
    })
  }
}

fn init_static() -> Result<()> {
  let log_level = env::var("LIBREDR_LOG_LEVEL").unwrap_or(String::from("info"));
  let worker_threads = env::var("LIBREDR_WORKER_THREADS").unwrap_or(String::from("1")).parse()?;
  RUNTIME.set(tokio::runtime::Builder::new_multi_thread().worker_threads(worker_threads).enable_all().build()?).ok();
  let fmt_layer = fmt::layer()
    .with_target(false);
  let filter_layer = EnvFilter::try_new(log_level)?;
  tracing_subscriber::registry()
    .with(filter_layer)
    .with(fmt_layer)
    .init();
  Ok(())
}

/// Initialize Python module.
///
/// Accept `LIBREDR_LOG_LEVEL` environment variable to set `log_level`.
/// * (default: info, feasible: debug, info, warn, error)
///
/// Accept `LIBREDR_WORKER_THREADS` environment variable to set `worker_threads`
/// * (default: 1)
#[pymodule]
#[pyo3(name = "libredr")]
pub fn py_libredr<'py>(py: Python<'py>, module: &Bound<'py, PyModule>) -> PyResult<()> {
  init_static()?;
  module.add("__author__", "Bohan Yu <ybh1998@protonmail.com>")?;
  module.add("__version__", format!("LibreDR {}", common::CLAP_LONG_VERSION))?;
  module.add_class::<PyLibreDR>()?;
  module.add_class::<PyGeometry>()?;
  py_camera(py, module)?;
  py_light_source(py, module)?;
  Ok(())
}
