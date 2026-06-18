from sympy import diff, simplify, latex, Add, Mul, Pow

def derivation_req(exp, varb):
    expr = exp
    var = varb
    
    step = {
        "derive": f"\\frac{{d}}{{d{var}}} ({latex(expr)})",
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
