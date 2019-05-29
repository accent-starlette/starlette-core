import inspect


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
