pub struct Compiler;

impl Compiler {
    pub fn compile(&self, input_string: &str) -> String {
        let tokens = self.tokenize(input_string);
        let ast = self.parse(tokens);
        let transformed = self.transform(ast);
        transformed.to_string()
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
