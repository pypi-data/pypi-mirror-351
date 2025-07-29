use std::fmt::Display;

use formualizer_core::parser::ASTNodeType as CoreASTNodeType;
use formualizer_core::tokenizer::{TokenSubType as CoreTokenSubType, TokenType as CoreTokenType};
use pyo3::prelude::*;
use pyo3_stub_gen::{create_exception, define_stub_info_gatherer, derive::*, module_variable};

/// Python-exposed token type enum
#[gen_stub_pyclass_enum]
#[pyclass(module = "formualizer")]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PyTokenType {
    Literal,
    Operand,
    Func,
    Array,
    Paren,
    Sep,
    OpPrefix,
    OpInfix,
    OpPostfix,
    Whitespace,
}


impl Display for PyTokenType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.__str__())
    }
}

#[pymethods]
impl PyTokenType {
    fn __str__(&self) -> &'static str {
        match self {
            PyTokenType::Literal => "Literal",
            PyTokenType::Operand => "Operand",
            PyTokenType::Func => "Func",
            PyTokenType::Array => "Array",
            PyTokenType::Paren => "Paren",
            PyTokenType::Sep => "Sep",
            PyTokenType::OpPrefix => "OpPrefix",
            PyTokenType::OpInfix => "OpInfix",
            PyTokenType::OpPostfix => "OpPostfix",
            PyTokenType::Whitespace => "Whitespace",
        }
    }

    fn __repr__(&self) -> String {
        format!("TokenType.{}", self.__str__())
    }
}

impl From<CoreTokenType> for PyTokenType {
    fn from(token_type: CoreTokenType) -> Self {
        match token_type {
            CoreTokenType::Literal => PyTokenType::Literal,
            CoreTokenType::Operand => PyTokenType::Operand,
            CoreTokenType::Func => PyTokenType::Func,
            CoreTokenType::Array => PyTokenType::Array,
            CoreTokenType::Paren => PyTokenType::Paren,
            CoreTokenType::Sep => PyTokenType::Sep,
            CoreTokenType::OpPrefix => PyTokenType::OpPrefix,
            CoreTokenType::OpInfix => PyTokenType::OpInfix,
            CoreTokenType::OpPostfix => PyTokenType::OpPostfix,
            CoreTokenType::Whitespace => PyTokenType::Whitespace,
        }
    }
}

impl From<PyTokenType> for CoreTokenType {
    fn from(py_token_type: PyTokenType) -> Self {
        match py_token_type {
            PyTokenType::Literal => CoreTokenType::Literal,
            PyTokenType::Operand => CoreTokenType::Operand,
            PyTokenType::Func => CoreTokenType::Func,
            PyTokenType::Array => CoreTokenType::Array,
            PyTokenType::Paren => CoreTokenType::Paren,
            PyTokenType::Sep => CoreTokenType::Sep,
            PyTokenType::OpPrefix => CoreTokenType::OpPrefix,
            PyTokenType::OpInfix => CoreTokenType::OpInfix,
            PyTokenType::OpPostfix => CoreTokenType::OpPostfix,
            PyTokenType::Whitespace => CoreTokenType::Whitespace,
        }
    }
}

/// Python-exposed token subtype enum
#[gen_stub_pyclass_enum]
#[pyclass(module = "formualizer")]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PyTokenSubType {
    None,
    Text,
    Number,
    Logical,
    Error,
    Range,
    Open,
    Close,
    Arg,
    Row,
}

impl Display for PyTokenSubType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.__str__())
    }
}

#[pymethods]
impl PyTokenSubType {
    fn __str__(&self) -> &'static str {
        match self {
            PyTokenSubType::None => "None",
            PyTokenSubType::Text => "Text",
            PyTokenSubType::Number => "Number",
            PyTokenSubType::Logical => "Logical",
            PyTokenSubType::Error => "Error",
            PyTokenSubType::Range => "Range",
            PyTokenSubType::Open => "Open",
            PyTokenSubType::Close => "Close",
            PyTokenSubType::Arg => "Arg",
            PyTokenSubType::Row => "Row",
        }
    }

    fn __repr__(&self) -> String {
        format!("TokenSubType.{}", self.__str__())
    }
}

impl From<CoreTokenSubType> for PyTokenSubType {
    fn from(subtype: CoreTokenSubType) -> Self {
        match subtype {
            CoreTokenSubType::None => PyTokenSubType::None,
            CoreTokenSubType::Text => PyTokenSubType::Text,
            CoreTokenSubType::Number => PyTokenSubType::Number,
            CoreTokenSubType::Logical => PyTokenSubType::Logical,
            CoreTokenSubType::Error => PyTokenSubType::Error,
            CoreTokenSubType::Range => PyTokenSubType::Range,
            CoreTokenSubType::Open => PyTokenSubType::Open,
            CoreTokenSubType::Close => PyTokenSubType::Close,
            CoreTokenSubType::Arg => PyTokenSubType::Arg,
            CoreTokenSubType::Row => PyTokenSubType::Row,
        }
    }
}

impl From<PyTokenSubType> for CoreTokenSubType {
    fn from(py_subtype: PyTokenSubType) -> Self {
        match py_subtype {
            PyTokenSubType::None => CoreTokenSubType::None,
            PyTokenSubType::Text => CoreTokenSubType::Text,
            PyTokenSubType::Number => CoreTokenSubType::Number,
            PyTokenSubType::Logical => CoreTokenSubType::Logical,
            PyTokenSubType::Error => CoreTokenSubType::Error,
            PyTokenSubType::Range => CoreTokenSubType::Range,
            PyTokenSubType::Open => CoreTokenSubType::Open,
            PyTokenSubType::Close => CoreTokenSubType::Close,
            PyTokenSubType::Arg => CoreTokenSubType::Arg,
            PyTokenSubType::Row => CoreTokenSubType::Row,
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTokenType>()?;
    m.add_class::<PyTokenSubType>()?;
    Ok(())
}
