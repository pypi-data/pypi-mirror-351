use crate::reference::{reference_type_to_py, ReferenceLike};
use crate::token::PyToken;
use formualizer_common::LiteralValue;
use formualizer_core::parser::{ASTNode, ASTNodeType};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3_stub_gen::{create_exception, define_stub_info_gatherer, derive::*, module_variable};

#[gen_stub_pyclass]
#[pyclass(module = "formualizer", name = "ASTNode")]
#[derive(Clone)]
pub struct PyASTNode {
    inner: ASTNode,
}

impl PyASTNode {
    pub fn new(inner: ASTNode) -> Self {
        PyASTNode { inner }
    }
}

#[gen_stub_pymethods]
#[pymethods]
impl PyASTNode {
    /// Get the pretty-printed representation of this AST
    fn pretty(&self) -> String {
        self.format_node(0)
    }

    /// Round-trips the node back to canonical Excel formula (with leading '=').
    pub fn to_formula(&self) -> String {
        let formula = formualizer_core::pretty::pretty_print(&self.inner);
        if formula.starts_with('=') {
            formula
        } else if !matches!(self.inner.node_type, ASTNodeType::Literal(_)) {
            format!("={}", formula)
        } else {
            formula
        }
    }

    /// Get a stable fingerprint hash of this AST structure
    fn fingerprint(&self) -> u64 {
        self.inner.fingerprint()
    }

    /// Get immediate children of this AST node
    fn children(&self) -> Vec<PyASTNode> {
        match &self.inner.node_type {
            ASTNodeType::UnaryOp { expr, .. } => {
                vec![PyASTNode::new((**expr).clone())]
            }
            ASTNodeType::BinaryOp { left, right, .. } => {
                vec![
                    PyASTNode::new((**left).clone()),
                    PyASTNode::new((**right).clone()),
                ]
            }
            ASTNodeType::Function { args, .. } => {
                args.iter().map(|arg| PyASTNode::new(arg.clone())).collect()
            }
            ASTNodeType::Array(rows) => rows
                .iter()
                .flat_map(|row| row.iter())
                .map(|cell| PyASTNode::new(cell.clone()))
                .collect(),
            _ => vec![],
        }
    }

    /// Walk through all references in this AST
    fn walk_refs(&self) -> PyRefWalker {
        let refs = self.collect_references();
        PyRefWalker { refs, index: 0 }
    }

    /// Convert AST to a dictionary representation
    fn to_dict(&self, py: Python<'_>) -> PyObject {
        self.node_to_dict(py, &self.inner)
    }

    /// Get the node type as a string
    fn node_type(&self) -> String {
        match &self.inner.node_type {
            ASTNodeType::Literal(_) => "Literal".to_string(),
            ASTNodeType::Reference { .. } => "Reference".to_string(),
            ASTNodeType::UnaryOp { .. } => "UnaryOp".to_string(),
            ASTNodeType::BinaryOp { .. } => "BinaryOp".to_string(),
            ASTNodeType::Function { .. } => "Function".to_string(),
            ASTNodeType::Array(_) => "Array".to_string(),
        }
    }

    /// Get the value for literal nodes
    fn get_literal_value(&self, py: Python<'_>) -> Option<PyObject> {
        match &self.inner.node_type {
            ASTNodeType::Literal(value) => Some(self.literal_value_to_py(py, value)),
            _ => None,
        }
    }

    /// Get the reference string for reference nodes
    fn get_reference_string(&self) -> Option<String> {
        match &self.inner.node_type {
            ASTNodeType::Reference { original, .. } => Some(original.clone()),
            _ => None,
        }
    }

    /// Get the reference as a rich object for reference nodes
    fn get_reference(&self) -> Option<ReferenceLike> {
        match &self.inner.node_type {
            ASTNodeType::Reference {
                reference,
                original,
            } => Some(reference_type_to_py(reference, original)),
            _ => None,
        }
    }

    /// Get the operator for unary/binary operation nodes
    fn get_operator(&self) -> Option<String> {
        match &self.inner.node_type {
            ASTNodeType::UnaryOp { op, .. } | ASTNodeType::BinaryOp { op, .. } => Some(op.clone()),
            _ => None,
        }
    }

    /// Get the function name for function nodes
    fn get_function_name(&self) -> Option<String> {
        match &self.inner.node_type {
            ASTNodeType::Function { name, .. } => Some(name.clone()),
            _ => None,
        }
    }

    /// Get the source token if available
    fn get_source_token(&self) -> Option<PyToken> {
        self.inner
            .source_token
            .as_ref()
            .map(|token| PyToken::new(token.clone()))
    }

    fn __repr__(&self) -> String {
        format!("ASTNode({})", self.to_formula())
    }

    fn __str__(&self) -> String {
        self.to_formula()
    }
}

impl PyASTNode {
    fn format_node(&self, indent: usize) -> String {
        let indent_str = "  ".repeat(indent);
        match &self.inner.node_type {
            ASTNodeType::Literal(value) => {
                format!(
                    "{}Literal({})",
                    indent_str,
                    self.format_literal_value(value)
                )
            }
            ASTNodeType::Reference { original, .. } => {
                format!("{}Reference({})", indent_str, original)
            }
            ASTNodeType::UnaryOp { op, expr } => {
                format!(
                    "{}UnaryOp({})\n{}",
                    indent_str,
                    op,
                    PyASTNode::new((**expr).clone()).format_node(indent + 1)
                )
            }
            ASTNodeType::BinaryOp { op, left, right } => {
                format!(
                    "{}BinaryOp({})\n{}\n{}",
                    indent_str,
                    op,
                    PyASTNode::new((**left).clone()).format_node(indent + 1),
                    PyASTNode::new((**right).clone()).format_node(indent + 1)
                )
            }
            ASTNodeType::Function { name, args } => {
                let mut result = format!("{}Function({})", indent_str, name);
                for arg in args {
                    result.push('\n');
                    result.push_str(&PyASTNode::new(arg.clone()).format_node(indent + 1));
                }
                result
            }
            ASTNodeType::Array(rows) => {
                let mut result = format!("{}Array", indent_str);
                for (row_idx, row) in rows.iter().enumerate() {
                    result.push_str(&format!("\n{}Row {}", "  ".repeat(indent + 1), row_idx));
                    for cell in row {
                        result.push('\n');
                        result.push_str(&PyASTNode::new(cell.clone()).format_node(indent + 2));
                    }
                }
                result
            }
        }
    }

    fn format_literal_value(&self, value: &LiteralValue) -> String {
        match value {
            LiteralValue::Int(i) => i.to_string(),
            LiteralValue::Number(n) => n.to_string(),
            LiteralValue::Text(s) => format!("\"{}\"", s),
            LiteralValue::Boolean(b) => b.to_string(),
            LiteralValue::Error(e) => format!("Error({})", e),
            LiteralValue::Date(d) => format!("Date({})", d),
            LiteralValue::DateTime(dt) => format!("DateTime({})", dt),
            LiteralValue::Time(t) => format!("Time({})", t),
            LiteralValue::Duration(dur) => format!("Duration({})", dur),
            LiteralValue::Array(arr) => format!("Array({:?})", arr),
            LiteralValue::Empty => "Empty".to_string(),
        }
    }

    fn collect_references(&self) -> Vec<ReferenceLike> {
        let mut refs = Vec::new();
        self.collect_refs_recursive(&mut refs);
        refs
    }

    fn collect_refs_recursive(&self, refs: &mut Vec<ReferenceLike>) {
        match &self.inner.node_type {
            ASTNodeType::Reference {
                reference,
                original,
            } => {
                refs.push(reference_type_to_py(reference, original));
            }
            ASTNodeType::UnaryOp { expr, .. } => {
                PyASTNode::new((**expr).clone()).collect_refs_recursive(refs);
            }
            ASTNodeType::BinaryOp { left, right, .. } => {
                PyASTNode::new((**left).clone()).collect_refs_recursive(refs);
                PyASTNode::new((**right).clone()).collect_refs_recursive(refs);
            }
            ASTNodeType::Function { args, .. } => {
                for arg in args {
                    PyASTNode::new(arg.clone()).collect_refs_recursive(refs);
                }
            }
            ASTNodeType::Array(rows) => {
                for row in rows {
                    for cell in row {
                        PyASTNode::new(cell.clone()).collect_refs_recursive(refs);
                    }
                }
            }
            _ => {}
        }
    }

    fn node_to_dict(&self, py: Python<'_>, node: &ASTNode) -> PyObject {
        let dict = PyDict::new(py);
        dict.set_item("node_type", self.node_type()).unwrap();

        match &node.node_type {
            ASTNodeType::Literal(value) => {
                dict.set_item("value", self.literal_value_to_py(py, value))
                    .unwrap();
            }
            ASTNodeType::Reference { original, .. } => {
                dict.set_item("reference", original).unwrap();
            }
            ASTNodeType::UnaryOp { op, expr } => {
                dict.set_item("operator", op).unwrap();
                dict.set_item("operand", PyASTNode::new((**expr).clone()).to_dict(py))
                    .unwrap();
            }
            ASTNodeType::BinaryOp { op, left, right } => {
                dict.set_item("operator", op).unwrap();
                dict.set_item("left", PyASTNode::new((**left).clone()).to_dict(py))
                    .unwrap();
                dict.set_item("right", PyASTNode::new((**right).clone()).to_dict(py))
                    .unwrap();
            }
            ASTNodeType::Function { name, args } => {
                dict.set_item("name", name).unwrap();
                let py_args: Vec<PyObject> = args
                    .iter()
                    .map(|arg| PyASTNode::new(arg.clone()).to_dict(py))
                    .collect();
                dict.set_item("args", py_args).unwrap();
            }
            ASTNodeType::Array(rows) => {
                let py_rows: Vec<Vec<PyObject>> = rows
                    .iter()
                    .map(|row| {
                        row.iter()
                            .map(|cell| PyASTNode::new(cell.clone()).to_dict(py))
                            .collect()
                    })
                    .collect();
                dict.set_item("rows", py_rows).unwrap();
            }
        }

        dict.into()
    }

    fn literal_value_to_py(&self, py: Python<'_>, value: &LiteralValue) -> PyObject {
        match value {
            LiteralValue::Int(i) => i.to_object(py),
            LiteralValue::Number(n) => n.to_object(py),
            LiteralValue::Text(s) => s.to_object(py),
            LiteralValue::Boolean(b) => b.to_object(py),
            LiteralValue::Error(e) => e.to_string().to_object(py),
            LiteralValue::Date(d) => d.to_string().to_object(py),
            LiteralValue::DateTime(dt) => dt.to_string().to_object(py),
            LiteralValue::Time(t) => t.to_string().to_object(py),
            LiteralValue::Duration(dur) => dur.to_string().to_object(py),
            LiteralValue::Array(arr) => {
                let py_arr: Vec<Vec<PyObject>> = arr
                    .iter()
                    .map(|row| {
                        row.iter()
                            .map(|cell| self.literal_value_to_py(py, cell))
                            .collect()
                    })
                    .collect();
                py_arr.to_object(py)
            }
            LiteralValue::Empty => py.None(),
        }
    }
}

#[gen_stub_pyclass]
#[pyclass(module = "formualizer")]
pub struct PyRefWalker {
    refs: Vec<ReferenceLike>,
    index: usize,
}

#[pymethods]
impl PyRefWalker {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<PyObject> {
        if slf.index < slf.refs.len() {
            let reference = slf.refs[slf.index].clone();
            slf.index += 1;
            Some(Python::with_gil(|py| reference.into_py(py)))
        } else {
            None
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyASTNode>()?;
    m.add_class::<PyRefWalker>()?;
    Ok(())
}
