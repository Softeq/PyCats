import paramiko

from scp import SCPClient


class SCP:
    """SCP uses a paramiko transport to send and receive files
    via the scp1 protocol.

    Examples:
        with SCP('10.10.10.10', 'user', 'password') as conn:
            conn.put('D:\temp\test.txt', '/home/user/temp/')
    """
    def __init__(self, host, user, password, port=22):
        """ Base initialization for class

        Args:
            host (str): Node IP to connect to.
            user (str): Node user.
            password (str): Node user password.
            port (int): Node port to connect to. Default - 22.
        """
        self.host = host
        self.user = user
        self.port = port
        self.password = password

    def __enter__(self):
        """Create an SSH session, connect to an SSH server and
        authenticate to it.

        Returns: An open SSH session.
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, username=self.user, port=self.port, password=self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close SSH session.
        Warning:
            Failure to do this may, in some situations, cause your Python
            interpreter to hang at shutdown (often due to race conditions).
            It's good practice to `close` your client objects anytime you're
            done using them, instead of relying on garbage collection."""
        self.ssh.close()

    def put(self, local_path, remote_path):
        """Transfer files and directories to remote node recursively.

        Args:
            local_path  (str | list): A single path, or a list of
                paths to be transferred.
            remote_path (str): Destination path in which to receive
                files or directories on the remote node.

        Returns: None.
        """
        scp_client = SCPClient(self.ssh.get_transport())
        scp_client.put(local_path, remote_path, recursive=True)

    def get(self, remote_path, local_path):
        """Transfer files and directories from remote node recursively.

        Args:
            remote_path (str | list): A path or a list of paths to
                retrieve from remote node.
            local_path  (str): Destination path in which to
                receive files or directories.

        Returns: None.
        """
        scp_client = SCPClient(self.ssh.get_transport())
        scp_client.get(remote_path, local_path, recursive=True)
