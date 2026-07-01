from sympy import diff, simplify, latex, Add, Mul, Pow

def derivation_req(exp, varb):
    expr = exp
    var = varb
    
    step = {
        "derive": f"\\frac{{d}}{{d{var}}} ({latex(expr)})",
        "rule": "",
        "substeps": []
    }

    # 1. Constant Case
    if not expr.has(var):
        step["rule"] = "Constant Rule"
        step["step_result"] = "0"
        return step

    # 2. Linear Variable Case (x)
    if expr == var:
        step["rule"] = "Derivative of the identity variable"
        step["step_result"] = "1"
        return step

    # 3. Sum/Difference Rule (Add)
    if isinstance(expr, Add):
        step["rule"] = "Sum Rule"
        arguments = expr.args
        for arg in arguments:
            step["substeps"].append(derivation_req(arg, var))
        step["step_result"] = latex(simplify(diff(expr, var)))
        return step

    # 4. Product Rule (Mul)
    if isinstance(expr, Mul):
        u = expr.args[0]
        v = Mul(*expr.args[1:])
        step["rule"] = "Product Rule"
        step["substeps"].append(derivation_req(u, var))
        step["substeps"].append(derivation_req(v, var))
        step["description"] = f"f'g + fg' where f={latex(u)} & g={latex(v)}"
        step["step_result"] = latex(diff(expr, var))
        return step

    # 5. Power Rule (Pow)
    if isinstance(expr, Pow):
        base, exp_val = expr.args
        if not exp_val.has(var): # x^n
            step["rule"] = "Power Rule"
            step["step_result"] = latex(simplify(diff(expr, var)))
            # If the base is composite, apply chain rule
            if base != var:
                step["rule"] = "Chain Rule with Power Rule"
                step["substeps"].append(derivation_req(base, var))
        return step

    # Default case (for trigonometric functions, etc.)
    step["rule"] = f"Derivative of elementary function ({type(expr).__name__})"
    step["step_result"] = latex(simplify(diff(expr, var)))
    return step
