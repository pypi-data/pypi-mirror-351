import ast
import astor
import black
from typing import Optional
from .gpt_commenter import generate_comment_gpt
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ImportRemover(ast.NodeTransformer):
    def __init__(self):
        self.used_names = set()
        self.imported_names = {}

    def visit_Name(self, node):
        self.used_names.add(node.id)
        return node

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_names[alias.asname or alias.name] = node
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_names[alias.asname or alias.name] = node
        return node

    def remove_unused_imports(self, tree):
        self.visit(tree)
        new_body = []
        
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.asname or alias.name for alias in node.names]
                if any(name in self.used_names for name in names):
                    new_body.append(node)
            else:
                new_body.append(node)
                
        tree.body = new_body
        return tree


class DocstringAdder(ast.NodeTransformer):
    def __init__(self, use_gpt: bool = False):
        self.use_gpt = use_gpt
        self.gpt_failures = 0

    def _generate_comment(self, node_type: str, node_name: str, node) -> str:
        if self.use_gpt and self.gpt_failures < 3:  # Limit GPT failures
            try:
                comment = generate_comment_gpt(node)
                if comment and not comment.startswith("Auto-generated comment"):
                    return comment
                self.gpt_failures += 1
            except Exception as e:
                logger.warning(f"GPT comment generation failed: {str(e)}")
                self.gpt_failures += 1
        return f"{node_type} {node_name}."

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if not self._has_docstring(node):
            comment = self._generate_comment("Function", node.name, node)
            self._add_docstring(node, comment)
        return node

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        if not self._has_docstring(node):
            comment = self._generate_comment("Class", node.name, node)
            self._add_docstring(node, comment)
        return node

    def _has_docstring(self, node) -> bool:
        return bool(node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str))

    def _add_docstring(self, node, comment: str):
        doc_node = ast.Expr(value=ast.Constant(value=comment))
        node.body.insert(0, doc_node)


def optimize_code(source_code: str, use_gpt: bool = False) -> str:
    """
    Optimize Python code with comprehensive error handling.
    
    Args:
        source_code: Python source code as string
        use_gpt: Whether to use AI for docstring generation
        
    Returns:
        Optimized code or original code with error comments if optimization fails
    """
    if not source_code.strip():
        raise ValueError("Empty code provided - nothing to optimize")

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        logger.error(f"Syntax error in code: {str(e)}")
        return f"# Syntax error: {str(e)}\n\n{source_code}"

    try:
        # Remove unused imports
        remover = ImportRemover()
        tree = remover.remove_unused_imports(tree)

        # Add docstrings
        doc_adder = DocstringAdder(use_gpt=use_gpt)
        tree = doc_adder.visit(tree)
        ast.fix_missing_locations(tree)

        # Convert AST back to code
        optimized_code = astor.to_source(tree)

        # Format with black (ignore if formatting fails)
        try:
            optimized_code = black.format_str(
                optimized_code,
                mode=black.Mode(
                    line_length=88,
                    string_normalization=True
                )
            )
        except Exception as e:
            logger.warning(f"Black formatting failed: {str(e)}")

        return optimized_code

    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        return f"# Optimization failed: {str(e)}\n\n{source_code}"