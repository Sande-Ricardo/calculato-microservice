import re
import sympy as sp

# Mapping of SymPy ODE classification keys to human-readable names
ODE_CLASSIFICATION_MAP = {
    "1st_linear": "First-Order Linear Ordinary Differential Equation",
    "separable": "Separable Ordinary Differential Equation",
    "Bernoulli": "Bernoulli Ordinary Differential Equation",
    "1st_exact": "Exact First-Order Ordinary Differential Equation",
    "nth_linear_constant_coeff_homogeneous": "Higher-Order Homogeneous Linear ODE with Constant Coefficients",
    "nth_linear_constant_coeff_undetermined_coefficients": "Higher-Order Non-Homogeneous Linear ODE with Constant Coefficients (Undetermined Coefficients)",
    "nth_linear_constant_coeff_variation_of_parameters": "Higher-Order Non-Homogeneous Linear ODE with Constant Coefficients (Variation of Parameters)",
    "2nd_linear_homogeneous_academic": "Second-Order Homogeneous Linear Ordinary Differential Equation",
    "homogeneous_1st": "Homogeneous First-Order Ordinary Differential Equation",
    "almost_linear": "Almost Linear First-Order Ordinary Differential Equation",
    "nth_order_reducible": "Reduced-Order Ordinary Differential Equation",
    "2nd_nonlinear_autonomous_conserved": "Second-Order Autonomous Conservative Non-linear ODE",
    "2nd_power_series_ordinary": "Second-Order Ordinary Power Series Method",
    "1st_power_series": "First-Order Power Series Method",
    "lie_group": "Lie Group Symmetry Method"
}

def normalize_derivatives_string(eq_str: str, dep_var: str = 'y', ind_var: str = 'x') -> str:
    """
    Preprocess and normalize different derivative notations (Leibniz, Newton, Lagrange/prime)
    into standard SymPy Derivative strings so they can be parsed by sympify.
    """
    # 1. LaTeX Leibniz notation: \frac{d^3y}{dx^3}, \frac{d^2y}{dx^2}, \frac{dy}{dx}
    eq_str = re.sub(rf'\\frac{{d\^3{dep_var}}}{{d{ind_var}\^3}}', f'Derivative({dep_var}({ind_var}), {ind_var}, 3)', eq_str)
    eq_str = re.sub(rf'\\frac{{d\^2{dep_var}}}{{d{ind_var}\^2}}', f'Derivative({dep_var}({ind_var}), {ind_var}, 2)', eq_str)
    eq_str = re.sub(rf'\\frac{{d{dep_var}}}{{d{ind_var}}}', f'Derivative({dep_var}({ind_var}), {ind_var})', eq_str)
    
    # 2. Text Leibniz notation: d^3y/dx^3, d^2y/dx^2, d2y/dx2, dy/dx
    eq_str = re.sub(rf'd\^3{dep_var}/d{ind_var}\^3', f'Derivative({dep_var}({ind_var}), {ind_var}, 3)', eq_str)
    eq_str = re.sub(rf'd\^2{dep_var}/d{ind_var}\^2', f'Derivative({dep_var}({ind_var}), {ind_var}, 2)', eq_str)
    eq_str = re.sub(rf'd2{dep_var}/d{ind_var}2', f'Derivative({dep_var}({ind_var}), {ind_var}, 2)', eq_str)
    eq_str = re.sub(rf'd{dep_var}/d{ind_var}', f'Derivative({dep_var}({ind_var}), {ind_var})', eq_str)
    
    # 3. Newton notation (dots): \ddot{y}, \dot{y}, yddot, ydot, y_dot, y_ddot
    eq_str = re.sub(rf'\\ddot{{{dep_var}}}', f'Derivative({dep_var}({ind_var}), {ind_var}, 2)', eq_str)
    eq_str = re.sub(rf'\\dot{{{dep_var}}}', f'Derivative({dep_var}({ind_var}), {ind_var})', eq_str)
    eq_str = re.sub(rf'{dep_var}ddot', f'Derivative({dep_var}({ind_var}), {ind_var}, 2)', eq_str)
    eq_str = re.sub(rf'{dep_var}dot', f'Derivative({dep_var}({ind_var}), {ind_var})', eq_str)
    eq_str = re.sub(rf'{dep_var}_dot', f'Derivative({dep_var}({ind_var}), {ind_var})', eq_str)
    eq_str = re.sub(rf'{dep_var}_ddot', f'Derivative({dep_var}({ind_var}), {ind_var}, 2)', eq_str)
    
    # 4. Prime notation with explicit independent variable: y''(x), y'(x)
    eq_str = re.sub(rf"{dep_var}'''\({ind_var}\)", f"Derivative({dep_var}({ind_var}), {ind_var}, 3)", eq_str)
    eq_str = re.sub(rf"{dep_var}''\({ind_var}\)", f"Derivative({dep_var}({ind_var}), {ind_var}, 2)", eq_str)
    eq_str = re.sub(rf"{dep_var}'\({ind_var}\)", f"Derivative({dep_var}({ind_var}), {ind_var})", eq_str)
    
    # 5. Prime notation without explicit independent variable: y''', y'', y'
    eq_str = re.sub(rf"{dep_var}'''", f"Derivative({dep_var}({ind_var}), {ind_var}, 3)", eq_str)
    eq_str = re.sub(rf"{dep_var}''", f"Derivative({dep_var}({ind_var}), {ind_var}, 2)", eq_str)
    eq_str = re.sub(rf"{dep_var}'", f"Derivative({dep_var}({ind_var}), {ind_var})", eq_str)
    
    # 6. Replace standalone dependent variable with dep_var(ind_var) (e.g. y -> y(x))
    # only if not already followed by (ind_var)
    eq_str = re.sub(rf'\b{dep_var}\b(?!\s*\(\s*{ind_var}\s*\))', f'{dep_var}({ind_var})', eq_str)
    
    return eq_str

def parse_ode_string(equation: str, dep_var: str = 'y', ind_var: str = 'x'):
    """
    Parse a string representation of an ODE into a SymPy Eq object.
    Raises ValueError if parsing fails.
    """
    try:
        normalized = normalize_derivatives_string(equation, dep_var, ind_var)
        
        # Split into LHS and RHS if '=' is present
        if '=' in normalized:
            parts = normalized.split('=')
            if len(parts) == 2:
                lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
            else:
                raise ValueError("Equation contains multiple '=' signs")
        else:
            lhs_str, rhs_str = normalized.strip(), "0"
            
        t_x = sp.Symbol(ind_var)
        t_y_func = sp.Function(dep_var)
        
        # Define local context for sympify
        locs = {
            ind_var: t_x,
            dep_var: t_y_func,
            'Derivative': sp.Derivative,
            'exp': sp.exp,
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'log': sp.log,
            'sqrt': sp.sqrt,
            'pi': sp.pi,
            'E': sp.E
        }
        
        lhs_expr = sp.sympify(lhs_str, locals=locs)
        rhs_expr = sp.sympify(rhs_str, locals=locs)
        
        return sp.Eq(lhs_expr, rhs_expr)
    except Exception as e:
        raise ValueError(f"Failed to parse ODE expression: {str(e)}")

# Pedagogical preference order (from simplest/most standard to more complex)
PEDAGOGICAL_ORDER = [
    "separable",
    "1st_linear",
    "1st_exact",
    "homogeneous_1st",
    "Bernoulli",
    "nth_linear_constant_coeff_homogeneous",
    "nth_linear_constant_coeff_undetermined_coefficients",
    "nth_linear_constant_coeff_variation_of_parameters",
    "2nd_linear_homogeneous_academic",
    "almost_linear",
    "nth_order_reducible",
    "2nd_nonlinear_autonomous_conserved",
    "2nd_power_series_ordinary",
    "1st_power_series",
    "lie_group"
]

def classify_ode(equation_expr, dep_var: str = 'y', ind_var: str = 'x'):
    """
    Classifies a parsed SymPy Eq ODE.
    Returns (primary_classification_id, primary_classification_name, all_classifications)
    """
    t_x = sp.Symbol(ind_var)
    t_y = sp.Function(dep_var)(t_x)
    
    classifications = sp.classify_ode(equation_expr, t_y)
    
    if not classifications:
        return "unknown", "Unknown Differential Equation", []
        
    # Exclude '_Integral' classifications as primary if regular ones exist
    valid_classifications = [c for c in classifications if not c.endswith('_Integral')]
    
    # Sort valid classifications based on pedagogical preference
    def get_preference_score(cls_id):
        try:
            return PEDAGOGICAL_ORDER.index(cls_id)
        except ValueError:
            return 999
            
    if valid_classifications:
        valid_classifications.sort(key=get_preference_score)
        primary_id = valid_classifications[0]
    else:
        # Fallback to general list if all are _Integral
        sorted_all = list(classifications)
        sorted_all.sort(key=get_preference_score)
        primary_id = sorted_all[0]
    
    # Map to human readable name
    primary_name = ODE_CLASSIFICATION_MAP.get(primary_id, primary_id.replace('_', ' ').title())
    
    return primary_id, primary_name, list(classifications)

def parse_initial_conditions(initial_conditions: dict, dep_var_func, ind_var_sym, dep_var: str = 'y', ind_var: str = 'x') -> dict:
    """
    Parse a dictionary of initial conditions into a SymPy ics dictionary.
    Supports formats like:
      - x0 / x_0 / t0 / t_0 for independent variable
      - y0 / y_0 / u0 for y(x0)
      - y0_prime / y0' / y_0_prime / y0_dot / dy_dx_0 for y'(x0)
      - y0_double_prime / y0'' / y_0_double_prime / y0_ddot / d2y_dx2_0 for y''(x0)
    """
    if not initial_conditions:
        return None
        
    def get_val(keys):
        for k in keys:
            if k in initial_conditions:
                try:
                    return sp.sympify(initial_conditions[k])
                except Exception:
                    pass
        return None
        
    x0 = get_val([f'{ind_var}0', f'{ind_var}_0', 'x0', 'x_0', 't0', 't_0'])
    if x0 is None:
        return None
        
    ics = {}
    
    y0 = get_val([f'{dep_var}0', f'{dep_var}_0', 'y0', 'y_0', 'u0', 'u_0'])
    if y0 is not None:
        ics[dep_var_func.subs(ind_var_sym, x0)] = y0
        
    y0_prime = get_val([
        f'{dep_var}0_prime', f'{dep_var}_0_prime', f"{dep_var}0'", f"{dep_var}_0'",
        'y0_prime', 'y_0_prime', 'y0_dot', 'y_0_dot', 'dy_dx_0'
    ])
    if y0_prime is not None:
        ics[dep_var_func.diff(ind_var_sym).subs(ind_var_sym, x0)] = y0_prime
        
    y0_db_prime = get_val([
        f'{dep_var}0_double_prime', f'{dep_var}_0_double_prime', f"{dep_var}0''", f"{dep_var}_0''",
        'y0_double_prime', 'y_0_double_prime', 'y0_ddot', 'y_0_ddot', 'd2y_dx2_0'
    ])
    if y0_db_prime is not None:
        ics[dep_var_func.diff(ind_var_sym, 2).subs(ind_var_sym, x0)] = y0_db_prime
        
    return ics

def solve_ode(equation_expr, dep_var: str = 'y', ind_var: str = 'x', initial_conditions: dict = None):
    """
    Solves the parsed SymPy Eq ODE.
    Returns a tuple (general_solution_expr, particular_solution_expr).
    Raises ValueError if solving fails.
    """
    t_x = sp.Symbol(ind_var)
    t_y = sp.Function(dep_var)(t_x)
    
    # 1. Solve General Solution
    try:
        general_sol = sp.dsolve(equation_expr, t_y)
    except Exception as e:
        raise ValueError(f"Failed to find general solution: {str(e)}")
        
    particular_sol = None
    
    # 2. Solve Particular Solution if initial conditions are provided
    if initial_conditions:
        ics = parse_initial_conditions(initial_conditions, t_y, t_x, dep_var, ind_var)
        if ics:
            try:
                particular_sol = sp.dsolve(equation_expr, t_y, ics=ics)
            except Exception as e:
                raise ValueError(f"Failed to find particular solution with initial conditions: {str(e)}")
                
    return general_sol, particular_sol

def format_solution(sol, use_latex: bool = False) -> str:
    """
    Formats a SymPy Eq (or list of Eq) into equation strings (e.g. y(x) = C1*exp(-2*x) + exp(x)/3).
    """
    if sol is None:
        return None
    if isinstance(sol, list):
        return [format_solution(s, use_latex) for s in sol]
    if isinstance(sol, sp.Eq):
        if use_latex:
            return f"{sp.latex(sol.lhs)} = {sp.latex(sol.rhs)}"
        else:
            return f"{str(sol.lhs)} = {str(sol.rhs)}"
    return str(sol)
