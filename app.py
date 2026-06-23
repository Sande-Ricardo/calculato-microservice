from flask import Flask, jsonify
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from sympy import symbols, diff, sympify
import sympy as sp

from engines.equation import process_equation
from engines.derivation import derivation_req
from engines.integration import integration_req
from engines.matrix import process_matrix

from schemas import DerivationRequestSchema, IntegrationRequestSchema, EquationRequestSchema, MatrixRequestSchema

app = Flask(__name__)

# Configure Flask-Smorest API
app.config['API_TITLE'] = 'Calculato Microservice API'
app.config['API_VERSION'] = 'v1'
app.config['OPENAPI_VERSION'] = '3.0.2'
app.config['OPENAPI_URL_PREFIX'] = '/'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/api/docs'
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/'

api = Api(app)

blp = Blueprint('computations', 'computations', url_prefix='/api', description='Mathematical Operations')

ALLOWED = {
    "e": sp.E, "pi": sp.pi, "I": sp.I,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt,
    "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
    "Abs": sp.Abs, "erf": sp.erf,
}

@blp.route('/derivation')
class Derivation(MethodView):
    @blp.arguments(DerivationRequestSchema)
    def post(self, args):
        """Calculates the derivative of a mathematical expression"""
        try:
            arg = sympify(args.get('expression', ''), locals=ALLOWED)
            var = symbols(args.get('variable', 'x'))
            response_data = derivation_req(arg, var)
            return jsonify(response_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@blp.route('/integration')
class Integration(MethodView):
    @blp.arguments(IntegrationRequestSchema)
    def post(self, args):
        """Calculates the integral of a mathematical expression"""
        try:
            response_data = integration_req(args)
            return jsonify(response_data)
        except Exception as e:
            print(f"Integration error: {e}")
            return jsonify({'Error': str(e)}), 400

@blp.route('/equation')
class Equation(MethodView):
    @blp.arguments(EquationRequestSchema)
    def post(self, args):
        """Solves, factorizes, expands, or simplifies algebraic equations"""
        try:
            response_data = process_equation(args)
            return jsonify(response_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@blp.route('/matrix')
class MatrixRoute(MethodView):
    @blp.arguments(MatrixRequestSchema)
    def post(self, args):
        """Performs linear algebra operations on matrices"""
        try:
            response_data = process_matrix(args)
            return jsonify(response_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

api.register_blueprint(blp)

@app.route('/tests')
def tests():
    return str(diff(sympify(str(5**2*2)+'*x**2'), "x"))

if __name__ == '__main__':
    app.run(debug=True)
