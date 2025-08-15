from flask import Flask, request, jsonify
from sympy import symbols, diff, integrate, sympify, latex
from sympy.integrals.manualintegrate import integral_steps
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
import sympy as sp

app = Flask(__name__)


# Funciones/constantes que exponemos al parser (ajusta según tus necesidades)
ALLOWED = {
    # constantes
    "E": sp.E, "pi": sp.pi, "I": sp.I,
    # funciones comunes
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
    "Abs": sp.Abs, "erf": sp.erf,
}

# x = symbols('x')  # Variable simbólica base

@app.route('/api/derivation', methods=['POST'])
def derive():
    data = request.get_json()
    return derivation_req(data)

@app.route('/api/integration', methods=['POST'])
def integrate_expr():
    data = request.get_json()
    return integration_req(data)

def derivation_req(data):
    expression = data.get('expression', '')
    var = data.get('variable', 'x')
    try:
        x = symbols(var)
        expr = sympify(expression)
        result = diff(expr, x)
        return jsonify({
            "expression": str(expr),
            "variable": str(x),
            "result": str(result),
            # "latex": f"${derive.latex()}$"
            "latex": latex(derive)
        })
        # expr = sympify(expression)
        # deriv = diff(expr, x)
        # return jsonify({'result': str(deriv)})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

def integration_req(data):
    expression = data.get('expression', '')
    var = data.get('variable', 'x')

    try:
        x = symbols(var)
        expr = sympify(expression)
        steps = integral_steps(expr, x)
        result = integrate(expr, x)
        
        return jsonify({
            "expression": str(expression),
            "variable": str(var),
            "result": str(result),
            # "latex": f"${result.latex()}$",
            "latex": latex(result),
            # "steps": [str(step) for step in steps]
            "steps": step_to_dict(steps) if steps else []
        })

        # expr = sympify(expression)
        # integ = integrate(expr, x)
        # return jsonify({'result': str(integ)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def step_to_dict(step):
    """Convierte un objeto de integral_steps a dict con LaTeX"""
    data = {
        "rule": step.__class__.__name__,
        "integrand": latex(step.integrand),
        "variable": str(step.variable),
    }
    if hasattr(step, "constant"):
        data["constant"] = latex(step.constant)
    if hasattr(step, "other"):
        data["other"] = latex(step.other)
    if hasattr(step, "base"):
        data["base"] = latex(step.base)
    if hasattr(step, "exp"):
        data["exp"] = latex(step.exp)
    if hasattr(step, "substep") and step.substep is not None:
        data["substep"] = step_to_dict(step.substep)
    if hasattr(step, "substeps") and step.substeps:
        data["substeps"] = [step_to_dict(s) for s in step.substeps]
    return data

@app.route('/tests')
def tests():
    return str(diff(sympify(str(5**2*2)+'*x**2'), x))

if __name__ == '__main__':
    app.run(debug=True)

