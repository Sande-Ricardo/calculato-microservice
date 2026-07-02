import pytest
import sympy as sp
from engines.ode import parse_ode_string, classify_ode

def test_parse_ode_string_notations():
    # 1. Lagrange / Prime notation
    eq1 = parse_ode_string("y' + 2*y = exp(x)")
    assert isinstance(eq1, sp.Eq)
    assert eq1.lhs.has(sp.Derivative)
    
    # 2. Lagrange with explicit independent variable
    eq2 = parse_ode_string("y''(x) - y(x) = 0")
    assert isinstance(eq2, sp.Eq)
    
    # 3. Leibniz notation
    eq3 = parse_ode_string("dy/dx + 2*y = exp(x)")
    assert isinstance(eq3, sp.Eq)
    
    eq4 = parse_ode_string("d^2y/dx^2 + 5*dy/dx = 0")
    assert isinstance(eq4, sp.Eq)
    
    # 4. LaTeX Leibniz
    eq5 = parse_ode_string(r"\frac{dy}{dx} - 3*y = 0")
    assert isinstance(eq5, sp.Eq)

    eq6 = parse_ode_string(r"\frac{d^2y}{dx^2} + y = 0")
    assert isinstance(eq6, sp.Eq)

    # 5. Newton/Dot notation
    eq7 = parse_ode_string("ydot + y = 0")
    assert isinstance(eq7, sp.Eq)
    
    eq8 = parse_ode_string(r"\ddot{y} + y = 0")
    assert isinstance(eq8, sp.Eq)

def test_parse_ode_different_variables():
    # Independent 't', Dependent 'u'
    eq = parse_ode_string("u_dot + 5*u = 0", dep_var='u', ind_var='t')
    assert isinstance(eq, sp.Eq)
    # The independent variable should be t
    t = sp.Symbol('t')
    u = sp.Function('u')(t)
    assert eq.lhs.has(t)
    assert eq.lhs.has(u)

def test_parse_ode_invalid():
    with pytest.raises(ValueError):
        parse_ode_string("y' + 2*y = exp(x) = 0")  # Multiple '='
    
    with pytest.raises(ValueError):
        parse_ode_string("y' + invalid_syntax_!!!!")  # Bad syntax

def test_classify_ode():
    # Test linear
    eq1 = parse_ode_string("y' + 2*y = exp(x)")
    primary_id, primary_name, all_classes = classify_ode(eq1)
    assert primary_id == "1st_linear"
    assert "1st_linear" in all_classes
    assert primary_name == "First-Order Linear Ordinary Differential Equation"
    
    # Test separable
    eq2 = parse_ode_string("dy/dx = y")
    primary_id, primary_name, all_classes = classify_ode(eq2)
    assert primary_id == "separable"
    assert primary_name == "Separable Ordinary Differential Equation"
    
    # Test homogeneous second order
    eq3 = parse_ode_string("y'' + y = 0")
    primary_id, primary_name, all_classes = classify_ode(eq3)
    assert primary_id == "nth_linear_constant_coeff_homogeneous"
    assert "nth_linear_constant_coeff_homogeneous" in all_classes
