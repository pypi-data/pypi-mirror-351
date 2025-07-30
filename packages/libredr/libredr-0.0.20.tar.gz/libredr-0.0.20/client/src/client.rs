use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use tracing::info;
use ndarray::prelude::*;
use anyhow::{Error, Result, bail, anyhow};
use common::message::*;
use common::geometry::Geometry;
use common::connection::Connection;

/// Rust interface for LibreDR client
#[derive(Debug)]
pub struct LibreDR {
  connection: Connection,
}

impl LibreDR {
  /// Construct `LibreDR` by connecting to LibreDR server\
  /// Return `Error` if connection failed\
  /// # Examples
  /// ```
  /// async {
  ///   let client_tcp = LibreDR::new(String::from("127.0.0.1:9001"), false, false).await?;
  ///   let client_unix = LibreDR::new(String::from("/var/run/libredr_client.sock"), true, false).await?;
  /// }
  /// ```
  pub async fn new(connect: String, unix: bool, tls: bool) -> Result<Self> {
    info!("LibreDR::new: Connecting to {connect}");
    let mut config: HashMap<String, String> = HashMap::new();
    config.insert(String::from("connect"), connect);
    config.insert(String::from("unix"), String::from(if unix { "true" } else { "false" }));
    config.insert(String::from("tls"), String::from(if tls { "true" } else { "false" }));
    Ok(LibreDR {
      connection: Connection::from_config(&config).await?,
    })
  }

  /// Receive messages, response `RequestData` task, until receive a different task
  async fn try_recv_msg_response_data(&mut self, data_cache: &DataCache) -> Result<Message> {
    loop {
      let msg_response = self.connection.recv_msg().await?;
      info!("LibreDR::try_recv_msg_response_data: msg_response {msg_response}");
      if let Message::RequestData(hash) = msg_response {
        let data = {
          let data_cache = data_cache.lock().expect("No task should panic");
          let entry = data_cache.get(&hash).ok_or(format!("Client: ray_tracing_forward: unexpected hash {hash}"));
          entry.map(|entry| {
            entry.1.to_owned()
          })
        };
        let msg_response = Message::ResponseData(Box::new(data.to_owned()));
        self.connection.send_msg(&msg_response).await?;
        data.map_err(Error::msg)?;
      } else {
        break Ok(msg_response);
      }
    }
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
  /// * `sample_per_pixel` - `sample_per_pixel_forward`, `sample_per_pixel_backward`
  /// * `max_bounce` - `max_bounce_forward`, `max_bounce_backward`, `max_bounce_low_discrepancy`, `skip_bounce`
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
  /// * if `camera_space` is `true`
  ///   * render image 3 * `image_shape`
  /// * if `camera_space` is `false`, add another
  ///   * ray texture coordinate 2 * `image_shape`
  ///   * ray depth (Euclidean distance) 1 * `image_shape`
  ///   * ray normal 3 * `image_shape`
  #[allow(clippy::too_many_arguments)]
  pub async fn ray_tracing_forward(&mut self,
      geometry: &Geometry,
      geometry_data_cache: &DataCache,
      ray: ArrayD<f32>,
      texture: Array3<f32>,
      envmap: Array4<f32>,
      sample_per_pixel: (usize, usize),
      max_bounce: (usize, usize, usize, usize),
      switches: (u8, u8, u8, u8),
      clip_near: (f32, f32, f32),
      camera_space: bool,
      requires_grad: bool,
      srand: i32,
      low_discrepancy: u32) -> Result<ArrayD<f32>> {
    let input_shape = ray.shape().to_owned();
    assert!(input_shape.len() > 1, "ray_tracing_forward: ray should be at least 1D");
    let ray_channels_input = if camera_space { 33 } else { 18 };
    assert_eq!(input_shape[0], ray_channels_input,
      "ray_tracing_forward: ray channel: {}, expected: {}", input_shape[0], ray_channels_input);
    let ray = ray.into_shape([ray_channels_input, input_shape[1..].iter().product()])?;
    let mut data_cache_content = hashbrown::HashMap::new();
    {
      let geometry_data_cache = geometry_data_cache.lock().expect("No task should panic");
      data_cache_content.extend(geometry_data_cache.iter().map(|(k, v)| {
        (k.to_owned(), v.to_owned())
      }));
    }
    let ray_data = Data::RayData(ray);
    let ray_data_hash = ray_data.hash();
    data_cache_content.insert(ray_data_hash.to_owned(), (0, ray_data));
    let material_data = Data::MaterialData(texture, envmap);
    let material_data_hash = material_data.hash();
    data_cache_content.insert(material_data_hash.to_owned(), (0, material_data));
    let data_cache = Arc::new(Mutex::new(data_cache_content));
    let request = RequestRayTracingForward {
      geometry: geometry.to_owned(),
      ray: ray_data_hash,
      material: material_data_hash,
      sample_per_pixel,
      max_bounce,
      switches,
      clip_near,
      camera_space,
      requires_grad,
      srand,
      low_discrepancy
    };
    let msg_request = Message::RequestTask(RequestTask::RequestRayTracingForward(Box::new(request)));
    info!("LibreDR::ray_tracing_forward: msg_request {msg_request}");
    self.connection.send_msg(&msg_request).await?;
    let msg_response = self.try_recv_msg_response_data(&data_cache).await?;
    let Message::ResponseTask(response_task) = msg_response else {
      bail!("Unexpected response {msg_response}");
    };
    let response_task = response_task.map_err(Error::msg)?;
    let ResponseTask::ResponseRayTracingForward(response) = response_task else {
      bail!("Unexpected response {response_task}");
    };
    let mut output_shape = input_shape.to_owned();
    output_shape[0] = if camera_space { 3 } else { 9 };
    let response = response.render.into_shape(output_shape)?;
    Ok(response)
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
  #[allow(clippy::too_many_arguments)]
  pub async fn ray_tracing_backward(&mut self, d_ray: ArrayD<f32>) ->
      Result<(Array3<f32>, Array4<f32>, Option<ArrayD<f32>>)> {
    let input_shape = d_ray.shape().to_owned();
    assert!(input_shape.len() > 1, "ray_tracing_backward: d_ray should be at least 1D");
    assert_eq!(input_shape[0], 3,
      "ray_tracing_backward: d_ray channel: {}, expected: {}", input_shape[0], 3);
    let request = RequestRayTracingBackward { d_ray: d_ray.into_shape([3, input_shape[1..].iter().product()])? };
    let msg_request = Message::RequestTask(RequestTask::RequestRayTracingBackward(Box::new(request)));
    info!("LibreDR::ray_tracing_backward: msg_request {msg_request}");
    self.connection.send_msg(&msg_request).await?;
    let msg_response = self.connection.recv_msg().await?;
    info!("LibreDR::ray_tracing_backward: msg_response {msg_response}");
    let Message::ResponseTask(response_task) = msg_response else {
      bail!("Unexpected response {msg_response}");
    };
    let response_task = response_task.map_err(Error::msg)?;
    let ResponseTask::ResponseRayTracingBackward(response) = response_task else {
      bail!("Unexpected response {response_task}");
    };
    let d_ray_texture = response.d_ray_texture.map(|d_ray_texture| {
      let mut output_shape = input_shape.to_owned();
      output_shape[0] = 14;
      d_ray_texture.into_shape(output_shape)
    }).transpose()?;
    Ok((
      response.d_texture.ok_or(anyhow!("LibreDR::ray_tracing_backward: None d_texture returned from server"))?,
      response.d_envmap.ok_or(anyhow!("LibreDR::ray_tracing_backward: None d_envmap returned from server"))?,
      d_ray_texture))
  }

  /// Send [`Message::Close`] to server to close cleanly
  pub async fn close(&mut self) -> Result<()> {
    self.connection.send_msg(&Message::Close()).await
  }
}
