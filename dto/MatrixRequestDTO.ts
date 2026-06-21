export interface MatrixRequestDTO {
    matrix: string[][];
    operation: 'inverse' | 'determinant' | 'rref';
    mode?: 'symbolic' | 'numeric';
}
