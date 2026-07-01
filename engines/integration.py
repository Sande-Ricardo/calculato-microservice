from sympy import symbols, integrate, latex, sympify
from sympy.integrals.manualintegrate import integral_steps

def integration_req(data):
    expression = data.get('expression', '')
    var = data.get('variable', 'x')  
    
    expr = sympify(expression)
    x_symbol = symbols(var)
    
    steps = integral_steps(expr, x_symbol)
    result = integrate(expr, x_symbol)
    
    return {
        "expression": str(expression),
        "variable": str(var),
        "result": str(result),
        "latex": latex(result),
        "steps": step_to_dict(steps) if steps else []
    }

def step_to_dict(step):
    """Converts an integral_steps object to a dict with LaTeX"""
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
