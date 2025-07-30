//! LibreDR is an open-source ray-tracing differentiable renderer
#![warn(missing_docs)]
#![warn(missing_debug_implementations)]

use std::path::Path;
use std::collections::HashMap;
use std::collections::hash_map::Entry;
use configparser::ini::Ini;
use anyhow::{Error, Result};
#[cfg(all(not(target_env = "msvc"), feature = "jemalloc"))]
use tikv_jemallocator::Jemalloc;

/// Constants to configure `Render`
pub mod render;
/// `Message` type shared by Client, Server, and Worker
pub mod message;
/// `Connection` type shared by Client, Server, and Worker
pub mod connection;
/// `Geometry` type shared by Client, Server, and Worker
pub mod geometry;

#[cfg(all(not(target_env = "msvc"), feature = "jemalloc"))]
#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;

/// Global allocator for display
pub const ALLOCATOR: &str = if cfg!(all(not(target_env = "msvc"), feature = "jemalloc")) {
  "jemalloc"
} else {
  "default"
};

/// `CLAP_LONG_VERSION` for display
pub const CLAP_LONG_VERSION: &str = const_format::concatcp!(
  "LibreDR ", self::connection::build::CLAP_LONG_VERSION,
  "\nallocator:", ALLOCATOR);

/// Load an ini config file and merge it to the current config HashMap
pub fn add_config(config: &mut HashMap<String, HashMap<String, String>>,
    new_config_file: &Path) -> Result<()> {
  let new_config = Ini::new()
    .load(new_config_file)
    .map_err(|err| format!("add_config: Error loading `{}`: {err}", new_config_file.display()))
    .map_err(Error::msg)?;
  for (section_key, new_section) in new_config {
    let Entry::Occupied(mut section) = config.entry(section_key.to_owned()) else {
      eprintln!("add_config: Warning: unexpected section `{section_key}`");
      continue;
    };
    let section = section.get_mut();
    for (entry_key, value) in new_section {
      let Some(value) = value else {
        continue;
      };
      match section.entry(entry_key) {
        Entry::Occupied(mut entry) => entry.insert(value),
        Entry::Vacant(vacant) => {
          let entry_key = vacant.into_key();
          eprintln!("add_config: Warning: unexpected entry `{entry_key}` in section `{section_key}`");
          continue;
        },
      };
    }
  }
  Ok(())
}
