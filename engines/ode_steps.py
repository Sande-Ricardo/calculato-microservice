import sympy as sp
import re
from engines.ode import format_solution

def generate_ode_steps(equation_expr, primary_id: str, general_sol, particular_sol=None, dep_var: str = 'y', ind_var: str = 'x', initial_conditions: dict = None):
    """
    Generates educational step-by-step resolution steps for the ODE.
    Returns a list of dicts: [{"order": int, "description": str, "math_state": str}]
    """
    steps = []
    t_x = sp.Symbol(ind_var)
    t_y_func = sp.Function(dep_var)
    t_y = t_y_func(t_x)
    dydx = t_y.diff(t_x)
    
    # Extract LHS and RHS
    lhs = equation_expr.lhs
    rhs = equation_expr.rhs
    expr = sp.simplify(lhs - rhs)
    
    try:
        if primary_id == "1st_linear":
            # Standard form: y' + P(x)*y = Q(x)
            # Find coeff of dydx
            coeff_dydx = expr.coeff(dydx)
            if coeff_dydx != 0:
                normalized_expr = sp.simplify(expr / coeff_dydx)
            else:
                normalized_expr = expr
                
            P = sp.simplify(normalized_expr.diff(t_y))
            # Substitute y=0 and dydx=0 to get Q(x)
            Q = sp.simplify(-normalized_expr.subs({t_y: 0, dydx: 0}))
            
            steps.append({
                "order": 1,
                "description": f"Identify the equation as a first-order linear ODE in standard form: {dep_var}' + P({ind_var}){dep_var} = Q({ind_var}). Here we extract P({ind_var}) and Q({ind_var}).",
                "math_state": f"P({ind_var}) = {sp.latex(P)}, \\quad Q({ind_var}) = {sp.latex(Q)}"
            })
            
            # Integrating factor: u = exp(integrate(P, x))
            int_P = sp.integrate(P, t_x)
            u = sp.exp(int_P)
            steps.append({
                "order": 2,
                "description": f"Calculate the integrating factor u({ind_var}) = e^{{\\int P({ind_var}) d{ind_var}}}.",
                "math_state": f"u({ind_var}) = e^{{\\int {sp.latex(P)} d{ind_var}}} = {sp.latex(u)}"
            })
            
            # Multiply by u and integrate Q*u
            qu = Q * u
            int_qu = sp.integrate(qu, t_x)
            
            C1 = sp.Symbol('C1')
            steps.append({
                "order": 3,
                "description": f"Multiply the ODE by the integrating factor u({ind_var}), rewriting the LHS as (u({ind_var}) {dep_var})', and integrate both sides.",
                "math_state": f"{dep_var}({ind_var}) {sp.latex(u)} = \\int {sp.latex(qu)} d{ind_var} = {sp.latex(int_qu)} + C_1"
            })
            
            formatted_gen = format_solution(general_sol, use_latex=True)
            steps.append({
                "order": 4,
                "description": f"Divide by the integrating factor u({ind_var}) to isolate {dep_var}({ind_var}) and find the general solution.",
                "math_state": formatted_gen
            })
            
            if particular_sol is not None and initial_conditions:
                # Solve for C1
                x0 = sp.sympify(initial_conditions.get('x0', 0))
                y0 = sp.sympify(initial_conditions.get('y0', 0))
                # Substitute in general solution: y(x) = (C1 + int_qu)/u
                # We can write: y0 = (C1 + int_qu.subs(x, x0)) / u.subs(x, x0)
                gen_sol_eq = general_sol
                if isinstance(gen_sol_eq, list):
                    gen_sol_eq = gen_sol_eq[0]
                
                eq_c1 = gen_sol_eq.subs({t_x: x0, t_y: y0})
                c1_vals = sp.solve(eq_c1, C1)
                c1_val_str = sp.latex(c1_vals[0]) if c1_vals else "0"
                
                formatted_part = format_solution(particular_sol, use_latex=True)
                steps.append({
                    "order": 5,
                    "description": f"Substitute the initial condition {dep_var}({sp.latex(x0)}) = {sp.latex(y0)} to solve for C_1, and find the particular solution.",
                    "math_state": f"C_1 = {c1_val_str} \\implies {formatted_part}"
                })
                
        elif primary_id == "separable":
            # Separable ODE: y' = g(x)*h(y) -> expr = dydx - g(x)*h(y) = 0
            # Let's extract g(x) and h(Y) using our Y symbol substitution
            Y = sp.Symbol('Y')
            # expr = dydx - f(x, y) = 0 -> dydx = f(x, y)
            # Find f(x, y) by solving expr for dydx
            f_expr = sp.solve(expr, dydx)
            if f_expr:
                f_xy = f_expr[0]
            else:
                # fallback
                f_xy = expr
                
            f_xY = f_xy.subs(t_y, Y)
            
            # Separate variables helper
            g, h = None, None
            for val_x in [0, 1, 2, -1]:
                for val_Y in [1, 2, 0, -1]:
                    try:
                        g_prop = f_xY.subs(Y, val_Y)
                        h_prop = f_xY.subs(t_x, val_x)
                        if g_prop.has(sp.nan, sp.oo, sp.zoo) or h_prop.has(sp.nan, sp.oo, sp.zoo):
                            continue
                        const = sp.simplify(f_xY / (g_prop * h_prop))
                        if not const.has(Y) and not const.has(t_x) and const != 0 and not const.has(sp.nan, sp.oo, sp.zoo):
                            g = sp.simplify(g_prop * const)
                            h = sp.simplify(h_prop)
                            break
                    except Exception:
                        continue
                if g is not None:
                    break
            
            if g is not None and h is not None:
                steps.append({
                    "order": 1,
                    "description": f"Identify the equation as separable. Separate the variables by placing all {dep_var} terms on the LHS and all {ind_var} terms on the RHS.",
                    "math_state": f"\\frac{{1}}{{{sp.latex(h.subs(Y, t_y))}}} d{dep_var} = {sp.latex(g)} d{ind_var}"
                })
                
                int_y_sym = sp.integrate(1 / h, Y)
                int_y = int_y_sym.subs(Y, t_y)
                int_x = sp.integrate(g, t_x)
                
                steps.append({
                    "order": 2,
                    "description": "Integrate both sides with respect to their respective variables.",
                    "math_state": f"\\int \\frac{{1}}{{{sp.latex(h.subs(Y, t_y))}}} d{dep_var} = \\int {sp.latex(g)} d{ind_var} \\implies {sp.latex(int_y)} = {sp.latex(int_x)} + C_1"
                })
            else:
                steps.append({
                    "order": 1,
                    "description": "Separate the variables of the ODE.",
                    "math_state": f"h({dep_var}) d{dep_var} = g({ind_var}) d{ind_var}"
                })
                
            formatted_gen = format_solution(general_sol, use_latex=True)
            steps.append({
                "order": 3,
                "description": f"Solve for {dep_var}({ind_var}) to find the general solution.",
                "math_state": formatted_gen
            })
            
            if particular_sol is not None and initial_conditions:
                formatted_part = format_solution(particular_sol, use_latex=True)
                x0 = sp.sympify(initial_conditions.get('x0', 0))
                y0 = sp.sympify(initial_conditions.get('y0', 0))
                steps.append({
                    "order": 4,
                    "description": f"Apply the initial condition {dep_var}({sp.latex(x0)}) = {sp.latex(y0)} to obtain the particular solution.",
                    "math_state": formatted_part
                })
                
        elif primary_id == "nth_linear_constant_coeff_homogeneous":
            # Homogeneous linear ODE with constant coefficients
            r = sp.Symbol('r')
            # 1. Replace Derivatives first
            expr_no_deriv = lhs.replace(
                lambda node: isinstance(node, sp.Derivative) and node.expr == t_y,
                lambda node: r ** sum(count for var, count in node.variable_count)
            )
            # 2. Replace y(x) with 1
            char_poly = expr_no_deriv.replace(
                lambda node: node == t_y,
                lambda node: sp.Integer(1)
            )
            char_eq = sp.Eq(char_poly, 0)
            
            steps.append({
                "order": 1,
                "description": f"Since this is a linear homogeneous ODE with constant coefficients, assume a solution of the form {dep_var} = e^{{r {ind_var}}} to write the characteristic equation.",
                "math_state": sp.latex(char_eq)
            })
            
            # Solve for r
            roots = sp.solve(char_poly, r)
            roots_latex = ", ".join([sp.latex(root) for root in roots])
            steps.append({
                "order": 2,
                "description": "Solve the characteristic equation to find the roots r.",
                "math_state": "r = \\\\left\\\\{ " + roots_latex + " \\\\right\\\\}"
            })
            
            formatted_gen = format_solution(general_sol, use_latex=True)
            steps.append({
                "order": 3,
                "description": f"Construct the general solution as a linear combination of fundamental solutions based on the roots.",
                "math_state": formatted_gen
            })
            
            if particular_sol is not None and initial_conditions:
                formatted_part = format_solution(particular_sol, use_latex=True)
                steps.append({
                    "order": 4,
                    "description": "Substitute the initial conditions to determine the values of the integration constants.",
                    "math_state": formatted_part
                })
                
        else:
            # Fallback / Generic ODE steps
            steps.append({
                "order": 1,
                "description": f"Identify the differential equation structure. SymPy classified this equation as: {primary_id}.",
                "math_state": f"\\text{{Classification: }} \\texttt{{{primary_id}}}"
            })
            
            formatted_gen = format_solution(general_sol, use_latex=True)
            steps.append({
                "order": 2,
                "description": "Integrate the differential equation symbolically using standard solving techniques.",
                "math_state": formatted_gen
            })
            
            if particular_sol is not None and initial_conditions:
                formatted_part = format_solution(particular_sol, use_latex=True)
                steps.append({
                    "order": 3,
                    "description": "Apply the initial value boundary conditions to resolve integration constants.",
                    "math_state": formatted_part
                })
                
    except Exception as e:
        # Fallback in case of step-generation error
        steps = [
            {
                "order": 1,
                "description": "Solve the ODE symbolically.",
                "math_state": format_solution(general_sol, use_latex=True)
            }
        ]
        if particular_sol is not None:
            steps.append({
                "order": 2,
                "description": "Apply initial conditions to find the particular solution.",
                "math_state": format_solution(particular_sol, use_latex=True)
            })
            
    return steps
