from trainloop_cli.eval_core.types import Sample
import re
import ast


def code_runs_correctly(sample: Sample) -> int:  # 1 = pass, 0 = fail
    content = sample.output["content"]

    # Extract code from code block
    pattern = r"```(?:python)?\s*\n(.*?)\n```"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        return 0

    code = matches[0].strip()

    try:
        # Parse the code to check syntax
        tree = ast.parse(code)

        # Check if there's a function named 'factorial'
        function_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "factorial":
                function_found = True
                break

        if not function_found:
            return 0

        # Execute the code and test the function
        namespace = {}
        exec(code, namespace)

        # Test cases
        factorial_func = namespace.get("factorial")
        if not factorial_func:
            return 0

        # Test basic functionality
        if factorial_func(0) != 1:
            return 0
        if factorial_func(1) != 1:
            return 0
        if factorial_func(5) != 120:
            return 0

        # Test error handling for negative numbers
        try:
            factorial_func(-1)
            # Should raise an error for negative numbers
            return 0
        except (ValueError, RecursionError):
            # Expected behavior
            pass

        return 1

    except Exception:
        return 0
