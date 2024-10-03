use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Token {
    Script = 1,
    Style = 2,
    Template = 3,
}

impl fmt::Display for Token {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Token::Script => write!(f, "Script"),
            Token::Style => write!(f, "Style"),
            Token::Template => write!(f, "Template"),
        }
    }
}

impl From<Token> for u8 {
    fn from(token: Token) -> Self {
        token as u8
    }
}

enum Element {
    Style(String),
    Script(String),
    Template(String),
    None,
}

pub fn tokenize(input: &str) -> Result<Vec<(Token, String)>, String> {
    println!("Input string: {:?}", input);
    let mut tokens = Vec::new();
    let mut remaining = input.trim();

    while !remaining.is_empty() {
        let element = extract_next_element(remaining);
        match element {
            Element::Style(content) => {
                println!("Extracted style: {:?}", content);
                tokens.push((Token::Style, content.clone()));
                remaining = &remaining[remaining.find("</style>").unwrap() + 8..];
            }
            Element::Script(content) => {
                println!("Extracted script: {:?}", content);
                tokens.push((Token::Script, content.clone()));
                remaining = &remaining[remaining.find("</script>").unwrap() + 9..];
            }
            Element::Template(content) => {
                println!("Extracted template: {:?}", content);
                tokens.push((Token::Template, content.clone()));
                let content_len = content.len();
                remaining = &remaining[content_len..];
            }
            Element::None => break,
        }
        println!("Remaining: {:?}", remaining);
    }

    if input.contains("<style>") && !input.contains("</style>") {
        return Err("Unclosed <style> tag".to_string());
    }
    if input.contains("<script>") && !input.contains("</script>") {
        return Err("Unclosed <script> tag".to_string());
    }

    println!("Final tokens: {:?}", tokens);
    Ok(tokens)
}

fn extract_next_element(input: &str) -> Element {
    if input.starts_with("<style>") {
        extract_style(input)
            .map(Element::Style)
            .unwrap_or(Element::None)
    } else if input.starts_with("<script>") {
        extract_script(input)
            .map(Element::Script)
            .unwrap_or(Element::None)
    } else {
        let (template, _) = extract_template(input);
        if template.is_empty() {
            Element::None
        } else {
            Element::Template(template.to_string())
        }
    }
}

fn extract_template(input: &str) -> (&str, &str) {
    let style_index = input.find("<style>");
    let script_index = input.find("<script>");

    match (style_index, script_index) {
        (Some(s), Some(c)) => input.split_at(s.min(c)),
        (Some(s), None) => input.split_at(s),
        (None, Some(c)) => input.split_at(c),
        (None, None) => (input, ""),
    }
}

fn extract_script(input: &str) -> Option<String> {
    extract_between(input, "<script>", "</script>")
}

fn extract_style(input: &str) -> Option<String> {
    extract_between(input, "<style>", "</style>")
}

fn extract_between(input: &str, start: &str, end: &str) -> Option<String> {
    input.find(start).and_then(|i| {
        let rest = &input[i + start.len()..];
        rest.find(end).map(|j| {
            let result = rest[..j].trim().to_string();
            println!("Extracted between {:?} and {:?}: {:?}", start, end, result);
            result
        })
    })
}
