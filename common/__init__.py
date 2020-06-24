import pkgutil

# set list of all package names under common folder
# used to replace libs logger with scaf logger
__all__ = list(module for _, module, _ in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'))
