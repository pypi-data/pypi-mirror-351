use pyo3::prelude::*;

mod functional;
mod directional;

/// Functional light source models (Rust)
pub use self::functional::functional_envmap;

/// Directional light source models (Rust and Python)
pub use self::directional::{directional_envmap, py_directional_envmap};

/// All light source models (Python)
pub fn py_light_source<'py>(py: Python<'py>, parent_module: &Bound<'py, PyModule>) -> PyResult<()> {
  let module = PyModule::new(py, "light_source")?;
  module.add_function(wrap_pyfunction!(py_directional_envmap, &module)?)?;
  parent_module.add_submodule(&module)?;
  Ok(())
}
