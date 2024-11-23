use once_cell::sync::Lazy;
use regex::Regex;

const BIRD_TAG_PATTERN: &str = r"(?s)(?m)<bird:(\w+)([^>]*)(?:/>|>(.*?)</bird:\w+>)";

pub static BIRD_TAG_REGEX: Lazy<Regex> =
    Lazy::new(|| Regex::new(BIRD_TAG_PATTERN).expect("Failed to compile BIRD_TAG_REGEX"));

pub struct Compiler;

impl Compiler {
    pub fn compile<'a>(&self, input_string: &'a str) -> &'a str {
        let tokens = self.tokenize(input_string);
        let ast = self.parse(tokens);
        self.transform(ast)
    }

    fn tokenize<'a>(&self, input_string: &'a str) -> &'a str {
        input_string
    }

    fn parse<'a>(&self, tokens: &'a str) -> &'a str {
        tokens
    }

    fn transform<'a>(&self, ast: &'a str) -> &'a str {
        ast
    }
}
