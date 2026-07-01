import sympy as sp
from latex2sympy2 import latex2sympy

def parse_latex_input(latex_str):
    try:
        if "=" in latex_str:
            parts = latex_str.split("=")
            if len(parts) == 2:
                lhs = latex2sympy(parts[0].strip())
                rhs = latex2sympy(parts[1].strip())
                return sp.Eq(lhs, rhs)
        expr = latex2sympy(latex_str)
        return expr
    except Exception as e:
        raise ValueError(f"Invalid LaTeX format or unparseable expression: {str(e)}")

def solve_equation(expr, var, method, original_latex):
    if isinstance(expr, sp.Eq):
        eq = expr.lhs - expr.rhs
    else:
        eq = expr

    steps = []
    
    if method == 'factorization':
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
            roots = sp.solve(eq, var)
            final_result = [f"{sp.latex(var)} = {sp.latex(root)}" for root in roots]
            steps.append({
                "order": 1,
                "description": "Solve the equation directly.",
                "math_state": " \\quad \\text{or} \\quad ".join(final_result)
            })
    return {
        "status": "success",
        "original_expression": original_latex,
        "final_result": final_result,
        "steps": steps
    }

# Test factorization:
expr1 = parse_latex_input("x^2 - 5x + 6 = 0")
res1 = solve_equation(expr1, sp.symbols('x'), 'factorization', "x^2 - 5x + 6 = 0")
print("Factorization result:")
print(res1)

# Test quadratic formula:
expr2 = parse_latex_input("x^2 - 5x + 6 = 0")
res2 = solve_equation(expr2, sp.symbols('x'), 'quadratic_formula', "x^2 - 5x + 6 = 0")
print("\nQuadratic formula result:")
print(res2)
