import inspect
import ast
from typing import Any, Callable


def nameof(var: Any):
    # Try to extract the argument expression from the caller's source code
    try:
        frame = inspect.currentframe()
        if frame is not None and frame.f_back is not None:
            outer_frame = frame.f_back
            frameinfo = inspect.getframeinfo(outer_frame)
            code_context = frameinfo.code_context
            if code_context:
                call_line = code_context[0]
                if "." in call_line:
                    return call_line.split(".")[-1].strip().strip("()")
              
    except Exception:
        pass
    # Fallback to variable name logic
    frame = inspect.currentframe()
    if frame is not None and frame.f_back is not None:
        callers_local_vars = frame.f_back.f_locals.items()
        names = [name for name, val in callers_local_vars if val is var]
        if len(names) == 1:
            return names[0]
        elif len(names) > 1:
            return "_and_".join(names)
    
    raise ValueError("Could not determine variable name. Ensure the variable is defined in the caller's scope.")


def somefunc(firstparam: str, secondparam: int = 42) -> None:
    print(nameof(firstparam))
    print(nameof(secondparam))


somefunc("hello")