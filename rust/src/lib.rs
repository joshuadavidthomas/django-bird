use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

mod lexer;
use lexer::tokenize as rust_tokenize;

#[pyfunction]
fn tokenize(input_string: &str) -> PyResult<Vec<(u8, String)>> {
    println!("Python input: {:?}", input_string);
    let result = rust_tokenize(input_string)
        .map(|tokens| {
            let python_tokens: Vec<(u8, String)> =
                tokens.into_iter().map(|(t, s)| (t as u8, s)).collect();
            println!("Python output: {:?}", python_tokens);
            python_tokens
        })
        .map_err(PyValueError::new_err);
    println!("Python result: {:?}", result);
    result
}

#[pymodule]
fn bird_compiler(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(tokenize, m)?)?;
    Ok(())
}
