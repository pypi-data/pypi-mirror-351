import inspect
from typing import Any, Callable, Iterable, NotRequired, TypedDict, Union, cast

from invoke.context import Context
from invoke.tasks import Task


class Parameter(TypedDict):
    name: str
    help: NotRequired[str]
    default: NotRequired[Union[str, int, float, bool]]


type Parameters = Iterable[Parameter]
type Arguments = dict[str, Union[str, int, float, bool]]
type BodyCallable[T] = Callable[[Context, Arguments], T]


def create_task[T](
    body: BodyCallable[T], parameters: Iterable[Parameter] = []
) -> Task[Any]:
    task_body: BodyCallable[T] = _create_task_body(body, parameters)
    return Task(task_body)


def _create_task_body[T](
    body: BodyCallable[T], parameters: Parameters, docstring: str = ""
) -> BodyCallable[T]:
    # Construct the signature from parameters
    param_objects = [
        inspect.Parameter("context", inspect.Parameter.POSITIONAL_ONLY)
    ]
    for parameter in parameters:
        param = inspect.Parameter(
            parameter["name"],
            inspect.Parameter.KEYWORD_ONLY,
            default=parameter.get("default", None),
        )
        param_objects.append(param)

    sig = inspect.Signature(param_objects)

    def new_function(*args: Any, **kwargs: Any) -> T:
        # Bind the arguments to the parameters
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Execute the body
        return body(args[0], kwargs)

    # Copy the signature to the new function
    setattr(new_function, "__signature__", sig)
    # Copy the name and docstring
    new_function.__name__ = body.__name__
    new_function.__doc__ = docstring

    return cast(BodyCallable[T], new_function)
