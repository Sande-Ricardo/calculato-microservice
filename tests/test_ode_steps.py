import pytest
import sympy as sp
from engines.ode import parse_ode_string, classify_ode, solve_ode
from engines.ode_steps import generate_ode_steps

def test_generate_steps_1st_linear():
    eq = parse_ode_string("y' + 2*y = exp(x)")
    primary_id, primary_name, _ = classify_ode(eq)
    gen_sol, part_sol = solve_ode(eq, initial_conditions={"x0": 0, "y0": 1})
    
    steps = generate_ode_steps(
        eq, primary_id, gen_sol, part_sol,
        dep_var='y', ind_var='x',
        initial_conditions={"x0": 0, "y0": 1}
    )
    
    assert isinstance(steps, list)
    assert len(steps) >= 4
    
    # Check that step 1 contains P(x) and Q(x)
    assert steps[0]["order"] == 1
    assert "P(x)" in steps[0]["math_state"]
    assert "Q(x)" in steps[0]["math_state"]
    
    # Check that step 2 contains the integrating factor
    assert steps[1]["order"] == 2
    assert "u(x)" in steps[1]["math_state"]
    assert "e^{2 x}" in steps[1]["math_state"] or "exp" in steps[1]["math_state"]
    
    # Check that step 5 exists for particular solution
    assert steps[-1]["order"] == 5
    assert "C_1 =" in steps[-1]["math_state"]

def test_generate_steps_separable():
    eq = parse_ode_string("dy/dx = y")
    primary_id, _, _ = classify_ode(eq)
    gen_sol, part_sol = solve_ode(eq, initial_conditions={"x0": 0, "y0": 2})
    
    steps = generate_ode_steps(
        eq, primary_id, gen_sol, part_sol,
        dep_var='y', ind_var='x',
        initial_conditions={"x0": 0, "y0": 2}
    )
    
    assert isinstance(steps, list)
    assert len(steps) >= 3
    
    # Check variables are separated
    assert "d y" in steps[0]["math_state"] or "dy" in steps[0]["math_state"]
    
    # Check integral step
    assert "C_1" in steps[1]["math_state"]
    assert "log" in steps[1]["math_state"] or "ln" in steps[1]["math_state"]

def test_generate_steps_homogeneous_higher_order():
    eq = parse_ode_string("y'' + 3*y' + 2*y = 0")
    primary_id, _, _ = classify_ode(eq)
    gen_sol, part_sol = solve_ode(eq, initial_conditions={"x0": 0, "y0": 1, "y0_prime": 2})
    
    steps = generate_ode_steps(
        eq, primary_id, gen_sol, part_sol,
        dep_var='y', ind_var='x',
        initial_conditions={"x0": 0, "y0": 1, "y0_prime": 2}
    )
    
    assert isinstance(steps, list)
    assert len(steps) >= 4
    
    # Step 1 is characteristic equation
    assert "r^{2}" in steps[0]["math_state"] or "r**2" in steps[0]["math_state"]
    assert "= 0" in steps[0]["math_state"]
    
    # Step 2 is roots
    assert "-2" in steps[1]["math_state"]
    assert "-1" in steps[1]["math_state"]

def test_generate_steps_fallback():
    # Let's write an exact equation y' = - (2*x*y + y**2) / (x**2 + 2*x*y)
    # y' + (2*x*y + y**2)/(x**2 + 2*x*y) = 0
    # classified as 1st_exact
    eq = parse_ode_string("y' + (2*x*y + y**2)/(x**2 + 2*x*y) = 0")
    primary_id, _, _ = classify_ode(eq)
    gen_sol, _ = solve_ode(eq)
    
    steps = generate_ode_steps(eq, primary_id, gen_sol)
    assert isinstance(steps, list)
    assert len(steps) >= 2
    assert primary_id in steps[0]["math_state"]
