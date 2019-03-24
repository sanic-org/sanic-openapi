from deepdiff import DeepDiff


def pytest_assertrepr_compare(op, left, right):
    if op == "==" and isinstance(left, dict) and isinstance(right, dict):
        diff = DeepDiff(left, right)
        if diff:
            result = ['Equal:']

            for k, v in diff.items():
                for x in v:
                    result.append("{} - {}".format(k, x))

            return result
