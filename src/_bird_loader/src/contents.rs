use std::fs;
use std::io;

use crate::compiler;

pub fn get_file_contents(file_path: &str, encoding: &str) -> io::Result<String> {
    let file_contents = load_file(file_path, encoding)?;

    if !compiler::BIRD_TAG_REGEX.is_match(&file_contents) {
        return Ok(file_contents);
    }

    let compiled_contents = compiler::Compiler.compile(&file_contents);
    Ok(compiled_contents.to_owned())
}

pub fn load_file(file_path: &str, encoding: &str) -> io::Result<String> {
    let bytes = fs::read(file_path)?;

    let encoding = encoding_rs::Encoding::for_label(encoding.as_bytes())
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "Invalid encoding"))?;

    let (decoded_str, _, had_errors) = encoding.decode(&bytes);
    if had_errors {
        Err(io::Error::new(io::ErrorKind::InvalidData, "Decoding error"))
    } else {
        Ok(decoded_str.into_owned())
    }
}
