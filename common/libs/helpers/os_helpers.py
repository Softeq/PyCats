import os
import time
import socket
import fnmatch
import platform

LINUX = 'Linux'
WIN = 'Windows'


def create_folder(folder):
    """Create folder inside the current directory.
    Args:
        folder (str): folder name

    Returns:
        Creates a folder with the specified name, otherwise raised OSError.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)


def create_subfolder(path, *subfolders):
    """Create sub-folder(s) inside the 'path' directory.
    Args:
        path  (str): An absolute path to the folder where sub-folder
            should be created.
        *subfolders (str | list): One or more sub-folder names.

    Returns: An absolute path to the created folder.
    """
    subfolder_path = os.path.join(path, *subfolders)
    create_folder(subfolder_path)
    return subfolder_path


def check_path_exists(path):
    """Check if file exists on the filesystem.

    Args:
        path (str): path to folder

    Returns: If folder do not exist raised OSError
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Directory or file '{path}' doesn't exist.")


def get_timestamp():
    """Get timestamp.

    Returns (str):
        Current timestamp in YYYY_mm_dd_HH_MM_SS format.

    """
    return f'{time.strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}'


def get_system_hostname():
    """ Get current hostname.

    Returns (str):
        Current hostname

    """
    return socket.gethostname()


def get_platform_type():
    """Get OS type.
    Returns (str):
         'Linux' for Linux, 'Windows' for Windows.
    """
    return platform.system()


def match_file_in_folder(folder, pattern):
    """Search for files in the specified folder by pattern. If any
    found, return a full path to the file. Otherwise, raise
    'FileNotFoundError' error.

    Args:
        folder  (str): An absolute path to the folder.
        pattern (str): Unix shell-style wildcards.

    Examples:
        >>> match_file_in_folder('/home/user/bin', '*main.dfw')
        '/home/user/bin/internal_ramdrive_main.dfw'
    """
    file_path = None
    for file_name in os.listdir(folder):
        if fnmatch.fnmatch(file_name, pattern):
            file_path = os.path.join(folder, file_name)
    if file_path is None:
        raise FileNotFoundError(f"File '{pattern}' not found in the '{folder}' directory.")
    return file_path


def generate_temp_execution_dirname(dirname):
    """Generate folder name with the following pattern:
        <dirname>_<hostname>_<timestamp>_
    """
    dirname = '_'.join(
        [dirname, get_system_hostname(), get_timestamp(), '/'])
    return dirname


TEMPDIR = generate_temp_execution_dirname('execution')
