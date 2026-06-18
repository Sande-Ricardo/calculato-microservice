import sympy as sp
from latex2sympy2 import latex2sympy

def parse_latex_input(latex_str):
    try:
        # latex2sympy converts the latex string to a sympy expression or equation
        expr = latex2sympy(latex_str)
        return expr
    except Exception as e:
        raise ValueError(f"Invalid LaTeX format or unparseable expression: {str(e)}")

def process_equation(data):
    latex_str = data.get('expression', '')
    operation = data.get('operation', '')
    target_variable_str = data.get('target_variable', 'x')
    method = data.get('method', 'factorization')
    
    expr = parse_latex_input(latex_str)
    var = sp.symbols(target_variable_str)

    if operation == 'solve':
        return solve_equation(expr, var, method, latex_str)
    elif operation == 'factorize':
        return factorize_expression(expr, latex_str)
    elif operation == 'expand':
        return expand_expression(expr, latex_str)
    elif operation == 'simplify':
        return simplify_expression(expr, latex_str)
    else:
        raise ValueError(f"Unsupported operation: {operation}")

def solve_equation(expr, var, method, original_latex):
    # Ensure it's an equation format for SymPy solvers (expr = 0)
    if isinstance(expr, sp.Eq):
        eq = expr.lhs - expr.rhs
    else:
        eq = expr

    steps = []
    
    if method == 'factorization':
        # Factorization method step-by-step logic
        factored = sp.factor(eq)
        steps.append({
            "order": 1,
            "description": "Factor the polynomial.",
            "math_state": f"{sp.latex(factored)} = 0"
        })
        
        factors = factored.args if isinstance(factored, sp.Mul) else [factored]
        factors_latex = [f"{sp.latex(arg)} = 0" for arg in factors if arg.has(var)]
        
        if factors_latex:
            steps.append({
                "order": 2,
                "description": "Set each factor containing the variable to zero.",
                "math_state": " \\quad \\text{or} \\quad ".join(factors_latex)
            })
            
        roots = sp.solve(eq, var)
        roots_latex = [f"{sp.latex(var)} = {sp.latex(root)}" for root in roots]
        
        steps.append({
            "order": 3,
            "description": "Solve for the variable in each equation.",
            "math_state": " \\quad \\text{or} \\quad ".join(roots_latex)
        })
        final_result = roots_latex
        
    elif method == 'general_formula' or method == 'quadratic_formula':
        # Quadratic formula method step-by-step logic
        poly = sp.Poly(eq, var)
        if poly.degree() == 2:
            coeffs = poly.all_coeffs()
            a, b, c = coeffs[0], coeffs[1], coeffs[2]
            steps.append({
                "order": 1,
                "description": "Identify coefficients a, b, and c.",
                "math_state": f"a={sp.latex(a)}, b={sp.latex(b)}, c={sp.latex(c)}"
            })
            steps.append({
                "order": 2,
                "description": "Apply the quadratic formula.",
                "math_state": f"{sp.latex(var)} = \\frac{{-({sp.latex(b)}) \\pm \\sqrt{{({sp.latex(b)})^2 - 4({sp.latex(a)})({sp.latex(c)})}}}}{{2({sp.latex(a)})}}"
            })
            roots = sp.solve(eq, var)
            roots_latex = [f"{sp.latex(var)} = {sp.latex(root)}" for root in roots]
            steps.append({
                "order": 3,
                "description": "Calculate the roots.",
                "math_state": " \\quad \\text{or} \\quad ".join(roots_latex)
            })
            final_result = roots_latex
        else:
            # Fallback if not a quadratic polynomial
            roots = sp.solve(eq, var)
            final_result = [f"{sp.latex(var)} = {sp.latex(root)}" for root in roots]
            steps.append({
                "order": 1,
                "description": "Solve the equation directly.",
                "math_state": " \\quad \\text{or} \\quad ".join(final_result)
            })
    else:
        # Default solving method
        roots = sp.solve(eq, var)
        final_result = [f"{sp.latex(var)} = {sp.latex(root)}" for root in roots]
        steps.append({
            "order": 1,
            "description": "Solve the equation.",
            "math_state": " \\quad \\text{or} \\quad ".join(final_result) if final_result else "No solution"
        })

    return {
        "status": "success",
        "original_expression": original_latex,
        "final_result": final_result,
        "steps": steps
    }

def factorize_expression(expr, original_latex):
    steps = []
    factored = sp.factor(expr)
    steps.append({
        "order": 1,
        "description": "Factorize the mathematical expression.",
        "math_state": sp.latex(factored)
    })
    return {
        "status": "success",
        "original_expression": original_latex,
        "final_result": [sp.latex(factored)],
        "steps": steps
    }

def expand_expression(expr, original_latex):
    steps = []
    expanded = sp.expand(expr)
    steps.append({
        "order": 1,
        "description": "Expand the mathematical expression.",
        "math_state": sp.latex(expanded)
    })
    return {
        "status": "success",
        "original_expression": original_latex,
        "final_result": [sp.latex(expanded)],
        "steps": steps
    }

def simplify_expression(expr, original_latex):
    steps = []
    simplified = sp.simplify(expr)
    steps.append({
        "order": 1,
        "description": "Simplify the mathematical expression.",
        "math_state": sp.latex(simplified)
    })
    return {
        "status": "success",
        "original_expression": original_latex,
        "final_result": [sp.latex(simplified)],
        "steps": steps
    }
