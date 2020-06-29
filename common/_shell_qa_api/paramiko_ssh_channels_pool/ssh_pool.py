import paramiko
import logging

from common._libs.helpers.singleton import Singleton
from threading import Lock

logger = logging.getLogger(__name__)


def get_ssh_channel(host, user, password, port=22):
    """
    Main SSH channel getter.
    """
    return SSHConnection().get_connection(host, user, password, port)


class SSHConnection(metaclass=Singleton):
    """
    SSH connection pool class.
    """

    def __init__(self):
        """Basic initialization.
        """
        self.connection_pool = dict()
        self.lock = Lock()

    def __del__(self):
        """
        Close all connections in destructor
        """
        self._close_all_connections()

    def get_connection(self, host, user, password, port=22):
        """ Create new connection or return already existing connection

        Args:
            host (str): Remote hostname
            user (str): Remote user
            password (str): Remote password
            port (int): SSH port. Default = 22

        Returns:
            Connection pool object
        """

        with self.lock:
            key = self._make_key(host, user)
            if not (key in self.connection_pool.keys()):
                logger.debug(
                    "create new connection to {}".format(host))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                try:
                    ssh.connect(hostname=host, port=port,
                                username=user, password=password)
                except paramiko.ssh_exception.AuthenticationException:
                    logger.error(
                        "Authentication to host {} failed. Please "
                        "check your credentials.".format(host))
                    raise
                self.connection_pool[key] = ssh
            return self.connection_pool[key]

    @staticmethod
    def _make_key(host, user):
        """
            Method representing key access to remote host
        Args:
            host (str): Remote hostname
            user (str): Remote user

        """
        return "{user}@{ip}".format(user=user, ip=host)

    def _close_all_connections(self):
        """ This method removes all connections.
        """
        for key in self.connection_pool.keys():
            self.connection_pool[key].close()
        self.connection_pool = dict()

    def close_connection(self, host, user):
        """This function remove connection to specific host .

        Args:
            host (str): Remote hostname
            user (str): Remote user

        Returns:
            Connection to host is close
        """
        key = "{user}@{ip}".format(user=user, ip=host)
        connection = self.connection_pool.pop(key, None)
        if connection:
            connection.close()
