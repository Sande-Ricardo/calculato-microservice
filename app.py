from flask import Flask, request, jsonify
from sympy import symbols, diff, integrate, sympify

app = Flask(__name__)
x = symbols('x')  # Variable simbólica base

@app.route('/api/derive', methods=['POST'])
def derive():
    data = request.get_json()
    expression = data.get('expression', '')
    try:
        expr = sympify(expression)
        deriv = diff(expr, x)
        return jsonify({'result': str(deriv)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/integrate', methods=['POST'])
def integrate_expr():
    data = request.get_json()
    expression = data.get('expression', '')
    try:
        expr = sympify(expression)
        integ = integrate(expr, x)
        return jsonify({'result': str(integ)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/tests')
def tests():
    return str(diff(sympify(str(5**2*2)+'*x**2'), x))

if __name__ == '__main__':
    app.run(debug=True)
