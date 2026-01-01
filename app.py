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

app = Flask(__name__)


# Funciones/constantes que se expone al parser (ajustar según necesidd)
ALLOWED = {
    # constantes
    "e": sp.E, "pi": sp.pi, "I": sp.I,
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
    arg = sympify(data.get('expression', ''), locals=ALLOWED)
    var = symbols(data.get('variable', 'x'))
        
    return derivation_req(arg, var)

@app.route('/api/integration', methods=['POST'])
def integrate_expr():
    data = request.get_json()
    return integration_req(data)

def derivation_req(exp, varb):
    expr = exp
    var = varb
    
    try:
        
        step = {
            "derive": f"\\frac{{d}}{{d{var}}} ({latex(expr)})",
            # "result": latex(diff(expr, var)),
            # "sympify": str(expr),
            "rule": "",
            "substeps": []
        }

        # 1. Caso Constante
        if not expr.has(var):
            step["rule"] = "Constant Rule"
            step["step_result"] = "0"
            return step

        # 2. Caso Variable Lineal (x)
        if expr == var:
            step["rule"] = "Derivative of the identity variable"
            step["step_result"] = "1"
            return step

        # 3. Regla de la Suma/Resta (Add)
        if isinstance(expr, Add):
            step["rule"] = "Sum Rule"
            argumentos = expr.args
            for arg in argumentos:
                step["substeps"].append(derivation_req(arg, var))
            step["step_result"] = latex(simplify(diff(expr, var)))
            return step

        # 4. Regla del Producto (Mul)
        if isinstance(expr, Mul):
            # Separamos en dos partes para simplificar la explicación (u * v)
            u = expr.args[0]
            v = Mul(*expr.args[1:])
            step["rule"] = "Product Rule"
            step["substeps"].append(derivation_req(u, var))
            step["substeps"].append(derivation_req(v, var))
            step["description"] = f"f'g + fg' where f={latex(u)} & g={latex(v)}"
            step["step_result"] = latex(diff(expr, var))
            return step

        # 5. Regla de la Potencia (Pow)
        if isinstance(expr, Pow):
            base, exp_val = expr.args
            if not exp_val.has(var): # x^n
                step["rule"] = "Power Rule"
                step["step_result"] = latex(simplify(diff(expr, var)))
                # Si la base es compuesta, aplicar regla de la cadena
                if base != var:
                    step["rule"] = "Chain Rule with Power Rule"
                    step["substeps"].append(derivation_req(base, var))
            return step

        # Caso por defecto (para funciones trigonométricas, etc.)
        step["rule"] = f"Derivative of elementary function ({type(expr).__name__})"
        step["step_result"] = latex(simplify(diff(expr, var)))
        return step

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# def step_to_derive(expr,var):
#     # Aquí se pueden implementar reglas de derivación paso a paso
#     steps = []
#     if expr.is_Add:
#         steps.append({
#             "rule": "Add Rule",
#             # "formula": "d(u + v)/dx = du/dx + dv/dx",
#             "formula":f"\\frac{{d}}{{d{var}}} ({expr.args[0]}) + \\frac{{d}}{{d{var}}} ({expr.args[1]})"
#         })
#     elif expr.is_Mul:
#         u, v = expr.args[0], expr.args[1]
#         steps.append({
#             "rule": "Product Rule",
#             "formula": f"({diff(u, var)})({v}) + ({u})({diff(v, var)})"
#     })

#     elif expr.is_Pow:
#         base, exp = expr.args
#         steps.append({
#             "rule": "Power  Rule",
#             "formula": f"{exp} \cdot {base}^{{{exp-1}}} \cdot \\frac{{d}}{{d{var}}}({base})"
#     })
    
#     return steps

def integration_req(data):
    expression = data.get('expression', '')
    var = data.get('variable', 'x')  # Esto llega como texto (String), ej: "x"
    
    try:
        # 1. Convertir la expresión texto a matemáticas
        expr = sympify(expression)
        
        # 2. [CORRECCIÓN CRÍTICA] Convertir la variable texto a Símbolo matemático
        x_symbol = symbols(var)
        
        # 3. Usar el Símbolo (x_symbol) en lugar del texto (var)
        steps = integral_steps(expr, x_symbol)
        result = integrate(expr, x_symbol)
        
        return jsonify({
            "expression": str(expression),
            "variable": str(var),
            "result": str(result),
            "latex": latex(result),
            # Validamos si steps existe para evitar errores si la integral es muy compleja
            "steps": step_to_dict(steps) if steps else []
        })

    except Exception as e:
        # Tip: Imprime el error en la consola para verlo tú también mientras desarrollas
        print(f"Error en integración: {e}")
        return jsonify({'Error': str(e)}), 400
    # expression = data.get('expression', '')
    # var = data.get('variable', 'x')
    # try:
        
    #     expr = sympify(expression)
    #     steps = integral_steps(expr, var)
    #     result = integrate(expr, var)
        
    #     return jsonify({
    #         "expression": str(expression),
    #         "variable": str(var),
    #         "result": str(result),
    #         # "latex": f"${result.latex()}$",
    #         "latex": latex(result),
    #         # "steps": [str(step) for step in steps]
    #         "steps": step_to_dict(steps) if steps else []
    #     })

    #     # expr = sympify(expression)
    #     # integ = integrate(expr, x)
    #     # return jsonify({'result': str(integ)})
    # except Exception as e:
    #     return jsonify({'Error': str(e)}), 400

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
    return str(diff(sympify(str(5**2*2)+'*x**2'), "x"))

if __name__ == '__main__':
    app.run(debug=True)

