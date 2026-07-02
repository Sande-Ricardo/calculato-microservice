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
