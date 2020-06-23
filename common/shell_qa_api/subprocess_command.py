import logging
import subprocess

logger = logging.getLogger(__name__)


def _post_send_command_actions(command, exp_rc, out, err, rc):
    """Process command result output.

    Args:
        command (str): Shell or bash command
        exp_rc (list): Expected result
        out (byte): Console output
        err (byte): Stderr output
        rc (int): Result code

    Returns:
        (tuple): Formatted command output and error output
    """
    out1 = out.decode('utf-8').rstrip('\n').split('\n')
    err1 = err.decode('utf-8').rstrip('\n').split('\n')

    logger.debug("Output stream:")
    for line in out1:
        logger.debug("        |" + line)

    logger.debug("Error stream:")

    for line in err1:
        logger.debug("        |" + line)
    logger.debug(f"Command result: {rc}")

    if exp_rc is not None and not isinstance(exp_rc, list):
        exp_rc = [int(exp_rc)]
    elif exp_rc is not None:
        exp_rc = [int(item) for item in exp_rc]

    if exp_rc is not None:
        if rc not in exp_rc:
            raise AssertionError(
                "Error occurred  during '%s' execution: "
                "got rc='%s' but expected %s. %s " % (
                    command, rc, exp_rc, err1))
    return out1, err1


def subprocess_send_command_asynchronous(command, exp_rc=0, timeout=None):
    """
    Send command via shell asynchronous.

        Args:
            command (str): Shell or bash command
            exp_rc (int): expected result, 0 by default
            timeout (int): timeout to kill communicate process

        Returns: Promise object
    """

    logger.info(
        "Executing command %s , expecting rc %s..." % (
            command, exp_rc))
    sub_process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    class Promise:
        def __init__(self, sub_process, command, exp_rc=0, timeout=None):
            self.sub_process = sub_process
            self.command = command
            self.exp_rc = exp_rc
            self.timeout = timeout

    return Promise(sub_process, command, exp_rc, timeout)


def get_subprocess_command_result(promise):
    """
    get subprocess command result.

           Args:
               promise (Promise): Promise object

           Returns: output , error output , result
    """
    sub_process = promise.sub_process
    command = promise.command
    exp_rc = promise.exp_rc
    timeout = promise.timeout

    try:
        out, err = sub_process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        sub_process.kill()
        out, err = sub_process.communicate()
        rc = sub_process.returncode
        _post_send_command_actions(command, None, out, err, rc)
        raise
    rc = sub_process.returncode
    logger.info("Command executed.")
    out1, err1 = _post_send_command_actions(command, exp_rc, out, err, rc)
    return out1, err1, rc


def subprocess_send_command(command, exp_rc=0, timeout=None):
    """Send command via shell.

    Args:
        command (str): Shell or bash command
        exp_rc (int): expected result, 0 by default
        timeout (int): timeout to kill communicate process

    Returns: output , error output , result
    """
    promise = subprocess_send_command_asynchronous(command, exp_rc=exp_rc, timeout=timeout)
    return get_subprocess_command_result(promise)
