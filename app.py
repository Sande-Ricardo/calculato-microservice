from flask import Flask, request, jsonify
from sympy import symbols, diff, integrate, simplify, sympify, latex, Add, Mul, Pow, sin, cos, exp, log, Symbol, E
from sympy.integrals.manualintegrate import integral_steps
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
import sympy as sp

from engines.equation import process_equation
from engines.derivation import derivation_req
from engines.integration import integration_req
from engines.matrix import process_matrix

app = Flask(__name__)

# Functions/constants that are exposed to the parser (adjust as needed)
ALLOWED = {
    # constants
    "e": sp.E, "pi": sp.pi, "I": sp.I,
    # common functions
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
    "Abs": sp.Abs, "erf": sp.erf,
}

@app.route('/api/derivation', methods=['POST'])
def derive():
    data = request.get_json()
    try:
        arg = sympify(data.get('expression', ''), locals=ALLOWED)
        var = symbols(data.get('variable', 'x'))
        
        response_data = derivation_req(arg, var)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/integration', methods=['POST'])
def integrate_expr():
    data = request.get_json()
    try:
        response_data = integration_req(data)
        return jsonify(response_data)
    except Exception as e:
        print(f"Integration error: {e}")
        return jsonify({'Error': str(e)}), 400

@app.route('/api/equation', methods=['POST'])
def resolve_equation():
    data = request.get_json()
    try:
        response_data = process_equation(data)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/matrix', methods=['POST'])
def resolve_matrix():
    data = request.get_json()
    try:
        response_data = process_matrix(data)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tests')
def tests():
    return str(diff(sympify(str(5**2*2)+'*x**2'), "x"))

if __name__ == '__main__':
    app.run(debug=True)
