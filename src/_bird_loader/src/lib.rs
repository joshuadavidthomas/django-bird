use pyo3::exceptions::{PyFileNotFoundError, PyUnicodeDecodeError, PyValueError};
use pyo3::prelude::*;
use std::io;

mod compiler;
mod contents;

#[pyfunction]
fn get_contents(py: Python<'_>, file_path: &str, encoding: &str) -> PyResult<PyObject> {
    match contents::get_file_contents(file_path, encoding) {
        Ok(contents) => Ok(contents.to_object(py)),
        Err(e) => match e.kind() {
            io::ErrorKind::NotFound => Err(PyFileNotFoundError::new_err(e.to_string())),
            io::ErrorKind::InvalidData => Err(PyUnicodeDecodeError::new_err(e.to_string())),
            io::ErrorKind::InvalidInput => Err(PyValueError::new_err(e.to_string())),
            _ => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string())),
        },
    }
}

#[pymodule]
fn _bird_loader(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_contents, m)?)?;
    Ok(())
}
