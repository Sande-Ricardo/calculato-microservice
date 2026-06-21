from sympy import Matrix, latex, simplify
from sympy.matrices.common import NonInvertibleMatrixError

def process_matrix(data):
    matrix_data = data.get('matrix', [])
    operation = data.get('operation', '')
    mode = data.get('mode', 'symbolic')

    if not matrix_data:
        raise ValueError("Matrix data is missing or empty.")

    A = Matrix(matrix_data)

    if operation == 'inverse':
        return compute_inverse(A)
    elif operation == 'determinant':
        return compute_determinant(A)
    elif operation == 'rref':
        return compute_rref(A)
    else:
        raise ValueError(f"Unsupported operation: {operation}")

def compute_determinant(A):
    if A.rows != A.cols:
        raise ValueError("Determinant requires a square matrix.")
    
    det_val = simplify(A.det())
    
    steps = [
        {
            "order": 1,
            "description": "Calculamos el determinante de la matriz.",
            "math_state": f"\\det(A) = {latex(det_val)}"
        }
    ]
    
    return {
        "status": "success",
        "operation": "determinant",
        "result": [[str(det_val)]],
        "steps": steps
    }

def compute_inverse(A):
    if A.rows != A.cols:
        raise ValueError("Inverse requires a square matrix.")
    
    try:
        det_val = simplify(A.det())
        if det_val == 0:
            raise ValueError("El determinante es 0, la matriz no es invertible.")
            
        inv_A = A.inv()
        
        steps = [
            {
                "order": 1,
                "description": "Primero, calculamos el determinante de la matriz A. Si es diferente de cero, la inversa existe.",
                "math_state": f"\\det(A) = {latex(det_val)}"
            },
            {
                "order": 2,
                "description": "Calculamos la matriz inversa.",
                "math_state": f"A^{{-1}} = {latex(inv_A)}"
            }
        ]
        
        # Format result as a list of lists of strings
        result_matrix = [[str(inv_A[i, j]) for j in range(inv_A.cols)] for i in range(inv_A.rows)]
        
        return {
            "status": "success",
            "operation": "inverse",
            "result": result_matrix,
            "steps": steps
        }
    except NonInvertibleMatrixError:
        raise ValueError("El determinante es 0, la matriz no es invertible.")

def compute_rref(A):
    rref_matrix, pivot_cols = A.rref()
    
    steps = [
        {
            "order": 1,
            "description": "Aplicamos eliminación de Gauss-Jordan para llevar la matriz a su forma escalonada reducida.",
            "math_state": f"\\text{{RREF}}(A) = {latex(rref_matrix)}"
        }
    ]
    
    result_matrix = [[str(rref_matrix[i, j]) for j in range(rref_matrix.cols)] for i in range(rref_matrix.rows)]
    
    return {
        "status": "success",
        "operation": "rref",
        "result": result_matrix,
        "steps": steps
    }
