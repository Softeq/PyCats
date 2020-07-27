import logging
import copy
from typing import Any
from dataclasses import field, dataclass

logger = logging.getLogger(__name__)


class SKIP:
    """Tells model validator to skip field validation.

    Should be callable object according to dataclass field specification
    """
    def __call__(self, *args, **kwargs):
        pass


def pycats_dataclass(_cls=None, *, init=True, repr=False, eq=False, order=False, unsafe_hash=None, frozen=False):
    """Wrapper for dataclass decorator. Used to simplify syntax and usage
    by disable __repr__ and  __eq__ methods generation, adds the ability to skip key's type annotations by default
    and automatically wraps mutable fields to support @dataclass protocol.

    If type is omitted - typing.Any is used instead

    Returns:
        The same class as was passed in, with dunder methods
        added based on the fields defined in the class.
    """
    if _cls:
        if not _cls.__dict__.get("__annotations__"):
            setattr(_cls, "__annotations__", {})

        for key, value in _cls.__dict__.items():
            # check if value is dataclass method or private
            if key.startswith("_") or (callable(value) and 'lambda' not in value.__name__):
                continue

            # add default annotation if not specified
            if not _cls.__dict__.get("__annotations__").get(key):
                _cls.__dict__.get("__annotations__")[key] = Any

            # for mutable data types dataclass protocol requires this data as field.
            # because of iteration we need to create deepcopy of object
            if isinstance(value, (dict, set)):
                setattr(_cls, key, field(default_factory=lambda value=value: value))
            # for empty lists we need to pass list as a callable without arguments
            elif not value and isinstance(value, list):
                setattr(_cls, key, field(default_factory=list))
            # if we have some values in list we need to make it's copy before
            elif value and isinstance(value, list):
                setattr(_cls, key, field(default_factory=lambda value=value: copy.deepcopy(value)))
            # if the value if lambda function - do the same as for list - just call it
            elif callable(value) and 'lambda' in value.__name__:
                setattr(_cls, key, field(default_factory=value))

    return dataclass(_cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen)


def make_request_url(model):
    """Method with logic to create URL.
    Args:
        model: Request Model

    Returns:
        The same model with populated url field
    """
    model.url = model.base_url + model.resource
    return model


def obj_to_dict(obj, exclude_params=None):
    """Non recursively transformer object to dict
    """
    if not exclude_params:
        exclude_params = []
    return dict(
        (key, obj.__getattribute__(key)) for key in dir(obj)
        if not callable(obj.__getattribute__(key))
        and not key.startswith('_')
        and key not in exclude_params)


def dict_to_obj(obj, **kwargs):
    """Non recursively transformer dict to object
    """
    for a, b in kwargs.items():
        if isinstance(b, (list, tuple)):
            setattr(obj, a, [x for x in b])
        else:
            setattr(obj, a, b)
