import os
import glob
import pkgutil

# set list of all package names under common folder except facade
# used to replace libs logger with scaf logger
allowed_paths = glob.glob(os.path.join(os.path.dirname(__file__), "[!facade]*"))
__all__ = list(".".join((__name__, file_handler.path.split(__name__+"\\")[-1], module)) for file_handler, module, _ in
               pkgutil.walk_packages(path=allowed_paths))
