###########################
class dotdict(dict):
    """
    Dictionary with dot notation access to attributes.
    Example:
        d = dotdict({'a': 1})
        d.a == 1
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

###########################

def map_nested_dicts(ob, func):
    """
    Recursively apply a function to all non-dict values in a nested dictionary.

    Args:
        ob (dict): The dictionary to process.
        func (callable): Function to apply to each non-dict value.

    Returns:
        dict: The processed dictionary with the function applied to all non-dict values.
    """
    for k, v in ob.items():
        if isinstance(v, dict):
            ob[k] = dotdict(v)
            map_nested_dicts(ob[k], func)
        else:
            ob[k] = func(v)
    return ob

###########################

def read_mat_script(f):
    """
    Read a simple MATLAB .m script with variable assignments and return a dictionary of variables.

    Args:
        f (str): Path to the MATLAB script file.

    Returns:
        dict: Dictionary of variable names and their evaluated values.
    """
    variables = {}

    with open(f, 'r') as file:
        for line in file:
            # Strip whitespace from the beginning and end of the line
            line = line.strip()

            # Ignore empty lines, comments, and section headers
            if not line or line.startswith('%'):
                continue

            # Split the line at the equals sign
            parts = line.split(';')[0].split('=')

            # Check if the line is in the expected format
            if len(parts) == 2:
                var_name = parts[0].strip()
                var_value = parts[1].strip()

                # Attempt to evaluate the value, defaulting to the original string if unsuccessful
                try:
                    var_value = eval(var_value, {"__builtins__": {}}, variables)
                except Exception:
                    pass

                # Store the variable and its value in the dictionary
                variables[var_name] = var_value

    return variables
