import inspect
from importlib import import_module


def import_string(dotted_path: str):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """

    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class'
            % (module_path, class_name)
        ) from err


def method_has_no_args(meth):
    """Return True if a method only accepts 'self'."""

    count = len(
        [
            p
            for p in inspect.signature(meth).parameters.values()
            if p.kind == p.POSITIONAL_OR_KEYWORD
        ]
    )
    return count == 0 if inspect.ismethod(meth) else count == 1
