export interface EquationRequestDTO {
    expression: string;
    operation: 'solve' | 'factorize' | 'expand' | 'simplify';
    target_variable?: string;
    method?: 'factorization' | 'general_formula' | 'quadratic_formula' | 'default';
}
