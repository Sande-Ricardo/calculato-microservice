from marshmallow import Schema, fields

class DerivationRequestSchema(Schema):
    expression = fields.String(required=True, description="The mathematical expression to differentiate")
    variable = fields.String(load_default="x", description="The variable with respect to which the derivative is calculated")

class IntegrationRequestSchema(Schema):
    expression = fields.String(required=True, description="The mathematical expression to integrate")
    variable = fields.String(load_default="x", description="The integration variable")

class EquationRequestSchema(Schema):
    expression = fields.String(required=True, description="The equation or expression in LaTeX format")
    operation = fields.String(required=True, description="The operation to perform: 'solve', 'factorize', 'expand', or 'simplify'")
    target_variable = fields.String(load_default="x", description="The variable to solve for (applicable for 'solve')")
    method = fields.String(load_default="factorization", description="The specific solving method")

class MatrixRequestSchema(Schema):
    matrix = fields.List(fields.List(fields.String()), required=True, description="A 2D array representation of the matrix")
    operation = fields.String(required=True, description="The operation to perform: 'inverse', 'determinant', or 'rref'")
    mode = fields.String(load_default="symbolic", description="Resolution mode: 'symbolic' or 'numeric'")
