import os

from common import scaf
from common.shell_qa_api.subprocess_command import _post_send_command_actions
from common.shell_qa_api.paramiko_ssh_channels_pool.ssh_pool import get_ssh_channel

logger = scaf.get_logger(__name__)


def ssh_send_command_asynchronous(host_ip, user, password, command,
                                  exp_rc=0, port=22, timeout=None):
    """ Send command via ssh asynchronous.

        Args:
            host_ip (str): remote host IP
            user (str): remote host user, root by default
            password (str): remote host password
            command (str): shell command
            exp_rc (int): expected result, 0 by default
            port (int):  ssh-port, 22 by default
            timeout (int): timeout to close communication channel

        Returns: Promise object

        """
    logger.info("send command {0} to host {1}".format(command, host_ip))
    remote = PasswordSSH(host_ip, user, password, port)
    remote.call_asynchronous(command)

    class Promise:
        def __init__(self, connection, command, exp_rc=0, timeout=None):
            self.connection = connection
            self.command = command
            self.exp_rc = exp_rc
            self.timeout = timeout

    return Promise(remote, command, exp_rc, timeout)


def get_ssh_command_result(promise):
    """
        get ssh command result.

               Args:
                   promise (Promise): Promise object

               Returns: output , error output , result
        """

    remote = promise.connection
    command = promise.command
    exp_rc = promise.exp_rc
    timeout = promise.timeout

    out, err, rc = remote.get_result(timeout)
    logger.info("Command executed.")

    out1, err1 = _post_send_command_actions(command, exp_rc, out, err, rc)

    return out1, err1, rc


def ssh_send_command(host_ip, user, password, command, exp_rc=0, port=22, timeout=None):
    """ Send command via ssh.

    Args:
        host_ip (str): remote host IP
        user (str): remote host user, root by default
        password (str): remote host password
        command (str): shell command
        exp_rc (int): expected result, 0 by default
        port (int):  ssh-port, 22 by default
        timeout (int): timeout to close communication channel

    Returns: output , error output , result

    """

    promise = ssh_send_command_asynchronous(host_ip, user, password,
                                            command, exp_rc=exp_rc,
                                            port=port,
                                            timeout=timeout)
    return get_ssh_command_result(promise)


class PasswordSSH(object):
    """
    Class that provide password SSH access to remote host
    Usage:
    remote = PasswordSSH(host_ip, user, password, port)
    out, err, rc = remote(command)
    """

    def __init__(self, host, user, password, port):
        """
            Base initialization method
        Args:
            host (str): remote host IP
            user (str): remote host user
            password (str): remote host password
            port (int):  ssh-port, 22 by default
        """
        self.client = get_ssh_channel(host, user, password, port)
        self.stdout, self.stderr = None, None

    def call(self, command):
        """ Call self as a function.

        Args:
            command (str): shell command
        Returns:
            stdout for executing command
            stderr for executing command
            result code for executing command. If command success, rc = 0

        """
        self.call_asynchronous(command)
        return self.get_result()

    def call_asynchronous(self, command):
        _, self.stdout, self.stderr = self.client.exec_command(command)

    def get_result(self, timeout=None):
        self.stdout.channel.status_event.wait(timeout)
        if not self.stdout.channel.status_event.is_set():
            self.stdout.channel.close()
        rc = self.stdout.channel.exit_status
        out = self.stdout.read()
        err = self.stderr.read()
        self.stdout = None
        self.stderr = None
        return out, err, rc


def make_ssh_passwordless_access_to_host(host, user, password, host_port=22):
    """
    Copy ssh keys to remote host using login and password.
    """
    with open(os.path.join(os.path.expanduser('~'),
                           '.ssh/id_rsa.pub')) as mykey:
        key_pub = mykey.read()
    logger.debug(key_pub)

    cmd_list = ['find ~/.ssh -type d 2>/dev/null '
                '|| mkdir -p ~/.ssh && chmod 700 ~/.ssh',
                'echo "%s" >> ~/.ssh/authorized_keys' % key_pub,
                'chmod 600 ~/.ssh/authorized_keys',
                'chmod 700 ~/.ssh',
                'chown %s.%s -R ~/.ssh' % (user, user)]
    remote = PasswordSSH(host, user, password, host_port)
    for command in cmd_list:
        logger.debug(command)
        remote.call(command)
