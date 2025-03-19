def validate_formula(formula):
    # Basic validation to prevent unsafe operations
    forbidden = ['eval', 'exec', 'import', '__']
    for item in forbidden:
        if item in formula:
            raise ValueError(f"Formula contains forbidden term: {item}")
    return True

def calculate_custom(data, formula):
    # Replace 'x' with actual data in the formula
    formula = formula.replace('x', 'data')
    try:
        return eval(formula)
    except Exception as e:
        raise ValueError(f"Error calculating formula: {e}")