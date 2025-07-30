use std::collections::HashMap;
use uuid::Uuid;
use shadow_rs::shadow;
use tokio::net::TcpStream;
use tracing::{debug, warn};
#[cfg(unix)]
use tokio::net::UnixStream;
use anyhow::{Result, bail};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use super::message::Message;

shadow!(build);

#[allow(missing_docs)]
#[derive(Debug)]
pub enum Stream {
  TcpStream(TcpStream),
#[cfg(unix)]
  UnixStream(UnixStream),
}

#[allow(missing_docs)]
impl Stream {
  pub async fn read_exact(&mut self, buf: &mut [u8]) -> tokio::io::Result<usize> {
    match self {
      Stream::TcpStream(stream) => stream.read_exact(buf).await,
#[cfg(unix)]
      Stream::UnixStream(stream) => stream.read_exact(buf).await,
    }
  }
}

/// `Connection` with a random `uuid` and human-readable `description`
#[derive(Debug)]
pub struct Connection {
  uuid: Uuid,
  stream: Stream,
  description: String,
}

impl Connection {
  /// `uuid` is read-only
  pub fn uuid(&self) -> Uuid {
    self.uuid
  }

  /// `description` is read-only
  pub fn description(&self) -> &str {
    &self.description
  }

  async fn check_version(&mut self) -> Result<()> {
    let local_version = Message::Version(
      build::PKG_VERSION.to_owned(),
      build::SHORT_COMMIT.to_owned(),
      build::COMMIT_DATE.to_owned());
    debug!("Connection::check_version: local: {}", local_version);
    self.send_msg(&local_version).await?;
    let remote_version = self.recv_msg().await?;
    if let Message::Version(ver, git, _) = &remote_version {
      debug!("Connection::check_version: remote: {}", remote_version);
      if ver == build::PKG_VERSION {
        if git != build::SHORT_COMMIT {
          warn!("Connection::check_version: Version match, but git commit mismatch. \
            local: {}, remote: {}", local_version, remote_version);
        }
        return Ok(());
      }
      bail!("Connection::check_version: Version mismatch: local. {}, remote: {}", local_version, remote_version);
    }
    bail!("Connection::check_version: unexpected message {}", remote_version);
  }

  /// Construct `Connection` with random UUID
  pub async fn from_stream(stream: Stream, description: String) -> Result<Self> {
    let uuid = Uuid::new_v4();
    let mut connection = Connection {
      uuid,
      stream,
      description: format!("{description} - {uuid}"),
    };
    connection.check_version().await?;
    Ok(connection)
  }

  /// Construct `Connection` by connecting to LibreDR server.
  ///
  /// Return `Error` if connection failed
  /// # Examples
  /// ```
  /// async {
  ///   let mut config = HashMap::new();
  ///   config.insert(String::from("connect"), string::from("127.0.0.1:9000"));
  ///   config.insert(String::from("unix"), string::from("false"));
  ///   config.insert(String::from("tls"), string::from("false"));
  ///   let connection = Connection::from_config(&config).await?;
  /// }
  /// ```
  pub async fn from_config(config: &HashMap<String, String>) -> Result<Self> {
    let (stream, description) = match config["unix"].as_str() {
      "false" => {
        let stream = TcpStream::connect(config["connect"].to_owned()).await?;
        let description = format!("tcp://{} - Server", config["connect"]);
        (Stream::TcpStream(stream), description)
      }
#[cfg(unix)]
      "true" => {
        let stream = UnixStream::connect(config["connect"].to_owned()).await?;
        let description = format!("unix://{} - Server", config["connect"]);
        (Stream::UnixStream(stream), description)
      },
#[cfg(not(unix))]
      "true" => {
        bail!("Connection::new: Error: Unix socket is not supported on current platform");
      },
      other => {
        bail!("Connection::new: Error: unknown config unix: {}", other);
      }
    };
    let uuid = Uuid::new_v4();
    let mut connection = Connection {
      uuid,
      stream,
      description,
    };
    connection.check_version().await?;
    Ok(connection)
  }

  /// Send a `Message`
  pub async fn send_msg(&mut self, msg: &Message) -> Result<()> {
    debug!("Connection::send_msg: timer 0 - {} - Serializing", self.uuid);
    // let mut msg = rmp_serde::to_vec(msg)?;
    let mut msg = postcard::to_stdvec(msg)?;
    let msg_len: u64 = msg.len().try_into()?;
    let mut raw_msg = Vec::from(msg_len.to_le_bytes());
    raw_msg.append(&mut msg);
    debug!("Connection::send_msg: timer 1 - {} - Sending {msg_len} bytes", self.uuid);
    match &mut self.stream {
      Stream::TcpStream(stream) => stream.write_all(&raw_msg).await?,
#[cfg(unix)]
      Stream::UnixStream(stream) => stream.write_all(&raw_msg).await?,
    }
    debug!("Connection::send_msg: timer 2 - {} - Finished", self.uuid);
    Ok(())
  }

  /// Receive a `Message`
  pub async fn recv_msg(&mut self) -> Result<Message> {
    debug!("Connection::recv_msg: timer 0 - {} - Receiving", self.uuid);
    let mut size_buffer = [0u8; 8];
    self.stream.read_exact(&mut size_buffer).await?;
    let msg_len = u64::from_le_bytes(size_buffer);
    let mut read_buffer = vec![0; msg_len as usize];
    self.stream.read_exact(&mut read_buffer).await?;
    debug!("Connection::recv_msg: timer 1 - {} - Deserializing {msg_len} bytes", self.uuid);
    // let msg: Message = rmp_serde::from_slice(&read_buffer)?;
    let msg: Message = postcard::from_bytes(&read_buffer)?;
    debug!("Connection::recv_msg: timer 2 - {} - Finished", self.uuid);
    Ok(msg)
  }
}
