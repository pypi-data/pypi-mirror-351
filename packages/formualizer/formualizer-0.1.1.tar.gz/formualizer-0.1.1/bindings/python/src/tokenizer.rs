use crate::{errors::TokenizerError, token::PyToken};
use formualizer_core::Tokenizer;
use pyo3::prelude::*;
use pyo3_stub_gen::{create_exception, define_stub_info_gatherer, derive::*, module_variable};

#[gen_stub_pyclass]
#[pyclass(module = "formualizer")]
pub struct PyTokenizer {
    inner: Tokenizer,
}

impl PyTokenizer {
    pub fn new(inner: Tokenizer) -> Self {
        PyTokenizer { inner }
    }
}

#[gen_stub_pymethods]
#[pymethods]
impl PyTokenizer {
    #[new]
    pub fn from_formula(formula: &str) -> PyResult<Self> {
        let tokenizer = Tokenizer::new(formula)
            .map_err(|e| TokenizerError::new_with_pos(e.message, Some(e.pos)))?;
        Ok(PyTokenizer::new(tokenizer))
    }

    /// Get all tokens as a list
    pub fn tokens(&self) -> Vec<PyToken> {
        self.inner
            .items
            .iter()
            .map(|token| PyToken::new(token.clone()))
            .collect()
    }

    /// Reconstruct the original formula from tokens
    fn render(&self) -> String {
        self.inner.render()
    }

    /// Make the tokenizer iterable
    fn __iter__(slf: PyRef<'_, Self>) -> PyTokenizerIter {
        let tokens = slf.tokens();
        PyTokenizerIter { tokens, index: 0 }
    }

    fn __len__(&self) -> usize {
        self.inner.items.len()
    }

    fn __getitem__(&self, index: isize) -> PyResult<PyToken> {
        let len = self.inner.items.len() as isize;
        let idx = if index < 0 { len + index } else { index };

        if idx < 0 || idx >= len {
            Err(pyo3::exceptions::PyIndexError::new_err(
                "Index out of range",
            ))
        } else {
            Ok(PyToken::new(self.inner.items[idx as usize].clone()))
        }
    }

    fn __repr__(&self) -> String {
        format!("Tokenizer({} tokens)", self.inner.items.len())
    }
}

#[gen_stub_pyclass]
#[pyclass(module = "formualizer")]
pub struct PyTokenizerIter {
    tokens: Vec<PyToken>,
    index: usize,
}

#[pymethods]
impl PyTokenizerIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<PyToken> {
        if slf.index < slf.tokens.len() {
            let token = slf.tokens[slf.index].clone();
            slf.index += 1;
            Some(token)
        } else {
            None
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTokenizer>()?;
    m.add_class::<PyTokenizerIter>()?;
    Ok(())
}
