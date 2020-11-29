class Singleton(type):
    """
        Metaclass ensures that in a single-process application there will be a single instance
         of a certain class, and providing a global access point to this instance.

    Examples:
        from _libs.common.helpers.singleton import Singleton
        class Test(metaclass=Singleton):

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """ Call self as a function. """
        if cls.__name__ not in cls._instances:
            cls._instances[cls.__name__] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls.__name__]


def get_singleton_class(key_name, base_class):
    """
        Returns singleton class instance with specified name and inheritable base class
       from Singleton instances.
    Args:
        key_name (str): Class name
        base_class (str): Base class name
    """
    singleton_class = Singleton(
        f"{key_name}_{base_class.__name__}",
        base_class.__bases__, dict(base_class.__dict__))
    return singleton_class


def delete_singleton_object(class_obj):
    """Remove class instance with specified name and inheritable base class
       from Singleton instances.

    Args:
        class_obj (type): Class name
    """
    # todo: discuss
    # return Singleton._instances.pop(f"{key_name}_{base_class.__name__}", None)
    return Singleton._instances.pop(class_obj.__name__, None)


def delete_singleton_objects(prefix):
    """Remove class instances with specified prefix
       from Singleton instances.

    Args:
        prefix (str): Specified prefix name

    """
    old_instances = dict(Singleton._instances)
    new_instances = dict(old_instances)
    for key in old_instances.keys():
        if key.startswith(prefix):
            new_instances.pop(key, None)
    Singleton._instances = new_instances
