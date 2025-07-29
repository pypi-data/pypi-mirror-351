import json
from typing import List, Dict
from src.QMGeneric import QMValue
import ast
import operator


def add_calculated_metrics(qm_values: List[QMValue], metrics_definitions: List[Dict]):
    """Calculates all metrics defined in metrics_definition using the extracted metrics from qm_values.
    qm_values is passed by reference. Postprocessed metrics are added to it.

    Args:
        qm_values (List[QMValue]): List of extracted metrics
        metrics_definitions (List[Dict]): Definition of metrics that need to be calculated
    """

    for metrics_definition in metrics_definitions:
        value = evaluate_metric(qm_values, metrics_definition["formula"])
        value_cast = safe_cast(value, metrics_definition["type"])
        if value_cast == None:
            continue
        qmv = QMValue(metrics_definition, value_cast)
        qm_values.append(qmv)


def evaluate_metric(qm_values: List[QMValue], formula: str):
    """Evaluate the formula given a list of quality metrics values. The values referenced in the formula
    have to be present in the qm_values list

    Args:
        qm_values (List[QMValue]): List of extracted quality metrics
        formula (str): formula used to calculate the postprocessed metric
    """
    formula_replaced = formula
    for qm_value in qm_values:
        formula_replaced = formula_replaced.replace(
            f"{{{qm_value.derived_from}}}", str(qm_value.value)
        )
    if "{" in formula_replaced:
        raise Exception(
            f"Not all references could be replaced in formula: {formula}: {formula_replaced}"
        )
    return safe_eval(formula_replaced)


def safe_cast(value, to_type):
    """cast a value to to_type. If to_type is an array we return the first successful cast in the array"""
    if not isinstance(to_type, list):
        to_type = [to_type]
    
    cast_error = False
    for t in to_type:
        try:
            return t(value)
        except (ValueError, TypeError):
            cast_error = True
    
    if cast_error:
        tested_types = [t.__name__ for t in to_type]
        tested_types = ", ".join(tested_types)
        raise ValueError(f"Value {value} is not of type {tested_types}")


class SafeEval(ast.NodeVisitor):

    # Define the set of allowed operators
    @property
    def allowed_operators(self):
        return {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg,
        }

    # Define the set of allowed names (functions and constants)
    @property
    def allowed_names(self):
        return {"abs": abs, "max": max, "min": min, "pow": pow}

    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        elif isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if type(node.op) in self.allowed_operators:
                return self.allowed_operators[type(node.op)](left, right)
            else:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            if type(node.op) in self.allowed_operators:
                return self.allowed_operators[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        elif isinstance(node, ast.Constant):  # For Python 3.8+
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in self.allowed_names:
                return self.allowed_names[node.id]
            else:
                raise ValueError(f"Unsupported function or constant: {node.id}")
        elif isinstance(node, ast.Call):
            func = self.visit(node.func)
            args = [self.visit(arg) for arg in node.args]
            return func(*args)
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")


def safe_eval(expr):
    """
    Safely evaluate a mathematical expression.

    :param expr: str, mathematical expression to evaluate
    :return: result of the evaluated expression
    """
    try:
        parsed_expr = ast.parse(expr, mode="eval")
        evaluator = SafeEval()
        return evaluator.visit(parsed_expr)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {expr}") from e
