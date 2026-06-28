from marshmallow import Schema, fields

class DerivationRequestSchema(Schema):
    expression = fields.String(required=True, metadata={"description": "The mathematical expression to differentiate"})
    variable = fields.String(load_default="x", metadata={"description": "The variable with respect to which the derivative is calculated"})

class IntegrationRequestSchema(Schema):
    expression = fields.String(required=True, metadata={"description": "The mathematical expression to integrate"})
    variable = fields.String(load_default="x", metadata={"description": "The integration variable"})

class EquationRequestSchema(Schema):
    expression = fields.String(required=True, metadata={"description": "The equation or expression in LaTeX format"})
    operation = fields.String(required=True, metadata={"description": "The operation to perform: 'solve', 'factorize', 'expand', or 'simplify'"})
    target_variable = fields.String(load_default="x", metadata={"description": "The variable to solve for (applicable for 'solve')"})
    method = fields.String(load_default="factorization", metadata={"description": "The specific solving method"})

class MatrixRequestSchema(Schema):
    matrix = fields.List(fields.List(fields.String()), required=True, metadata={"description": "A 2D array representation of the matrix"})
    operation = fields.String(required=True, metadata={"description": "The operation to perform: 'inverse', 'determinant', or 'rref'"})
    mode = fields.String(load_default="symbolic", metadata={"description": "Resolution mode: 'symbolic' or 'numeric'"})

class DescriptiveStatsRequestSchema(Schema):
    dataset = fields.List(fields.Float(), required=True, metadata={"description": "The dataset to analyze"})
    sample = fields.Boolean(load_default=True, metadata={"description": "Indicates if the dataset represents a sample (true) or a population (false)"})

class ProbabilityRequestSchema(Schema):
    distribution = fields.String(required=True, metadata={"description": "The type of distribution ('normal', 't_student', 'binomial', 'poisson')"})
    parameters = fields.Dict(required=True, metadata={"description": "Distribution-specific parameters"})
    query_type = fields.String(required=True, metadata={"description": "Type of calculation query ('exact', 'cumulative_less', 'cumulative_greater', 'between')"})
    query_value = fields.Raw(required=True, metadata={"description": "The x value or range (2-element array) to evaluate"})
