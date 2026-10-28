"""Process-wide handle to the enabled add-on module.

The runner assigns ``MOD`` after installing the extension. Test helpers read it
at call time so importing this module does not require Blender.
"""

MOD = None


def addon():
    if MOD is None:
        raise RuntimeError("Add-on module is not loaded. Run tests/run_tests.py inside Blender.")
    return MOD
