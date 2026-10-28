"""Registry for headless Blender tests."""

TESTS = []


def blender_test(fn):
    TESTS.append(fn)
    return fn
