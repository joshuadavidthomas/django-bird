use encoding_rs::Encoding;
use once_cell::sync::OnceCell;
use pyo3::exceptions::{PyFileNotFoundError, PyUnicodeDecodeError};
use pyo3::prelude::*;
use regex::Regex;
use std::fs::File;
use std::io::{self, Read};

mod compiler;

const BIRD_PATTERN: &str = r"(?s)(?m)<bird:(\w+)([^>]*)(?:/>|>(.*?)</bird:\w+>)";

#[pyfunction]
fn get_contents(py: Python, file_path: &str, encoding: &str) -> PyResult<PyObject> {
    static BIRD_REGEX: OnceCell<Regex> = OnceCell::new();

    let bird_regex =
        BIRD_REGEX.get_or_init(|| Regex::new(BIRD_PATTERN).expect("Failed to compile BIRD_REGEX"));

    let result = (|| -> Result<String, io::Error> {
        let mut file = File::open(file_path)?;
        let mut bytes = Vec::new();
        file.read_to_end(&mut bytes)?;

        let encoding = Encoding::for_label(encoding.as_bytes())
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "Invalid encoding"))?;

        let (cow, _, had_errors) = encoding.decode(&bytes);
        if had_errors {
            return Err(io::Error::new(io::ErrorKind::InvalidData, "Decoding error"));
        }

        let contents = cow.into_owned();

        if !bird_regex.is_match(&contents) {
            Ok(contents)
        } else {
            let compiler = compiler::Compiler;
            let compiled_contents = compiler.compile(&contents);
            Ok(compiled_contents.to_string())
        }
    })();

    match result {
        Ok(contents) => Ok(contents.to_object(py)),
        Err(e) if e.kind() == io::ErrorKind::NotFound => {
            Err(PyFileNotFoundError::new_err(e.to_string()))
        }
        Err(e) if e.kind() == io::ErrorKind::InvalidData => {
            Err(PyUnicodeDecodeError::new_err(e.to_string()))
        }
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string())),
    }
}

#[pymodule]
fn _bird_loader(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_contents, m)?)?;
    Ok(())
}
