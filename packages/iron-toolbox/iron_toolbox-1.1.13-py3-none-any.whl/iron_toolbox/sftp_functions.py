import io
import pandas as pd
import paramiko

''' Funções para conexão e download/upload de arquivos para SFTP '''


def connect_sftp(hostname, username, password):
    """
        Args:
            hostname: the remote host to read the file from
            username: the username to login to the remote host with
            password: the user password to login into the remote host
        """

    # open an SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    # read the file using SFTP
    sftp = client.open_sftp()
    print(f'{hostname} Conectado!')
    return sftp


def disconnect_sftp(client):
    client.close()
    print(f'SFTP Desconectado!')


def from_sftp_to_df(client_sftp, remote_path):
    with io.BytesIO() as fl:
        client_sftp.getfo(remote_path, fl)
        fl.seek(0)
    return fl


def read_csv_sftp(hostname: str, username: str, password: str, remotepath: str, *args, **kwargs) -> pd.DataFrame:
    """
    Read a file from a remote host using SFTP over SSH.
    Args:
        hostname: the remote host to read the file from
        username: the username to login into the remote host with
        password: the user password to login into the remote host
        remotepath: the path of the remote file to read
        *args: positional arguments to pass to pd.read_csv
        **kwargs: keyword arguments to pass to pd.read_csv
    Returns:
        a pandas DataFrame with data loaded from the remote host
    """
    # open an SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    # read the file using SFTP
    sftp = client.open_sftp()
    remote_file = sftp.open(remotepath)
    dataframe = pd.read_csv(remote_file, *args, **kwargs)
    remote_file.close()
    # close the connections
    sftp.close()
    client.close()
    return dataframe


# def execute_command(self, commands):
#     """Execute a command on the remote host.Return a tuple containing
#     an integer status and a two strings, the first containing stdout
#     and the second containing stderr from the command."""
#     self.ssh_output = None
#     result_flag = True
#     try:
#         if self.connect():
#             for command in commands:
#                 print("Executing command --> {}".format(command))
#                 stdin, stdout, stderr = self.client.exec_command(command, timeout=10)
#                 self.ssh_output = stdout.read()
#                 self.ssh_error = stderr.read()
#                 if self.ssh_error:
#                     print("Problem occurred while running command:" + command + " The error is " + self.ssh_error)
#                     result_flag = False
#                 else:
#                     print("Command execution completed successfully", command)
#                 self.client.close()
#         else:
#             print("Could not establish SSH connection")
#             result_flag = False
#     except socket.timeout as e:
#         print("Command timed out.", command)
#         self.client.close()
#         result_flag = False
#     except paramiko.SSHException:
#         print("Failed to execute the command!", command)
#         self.client.close()
#         result_flag = False
#
#     return result_flag
#
# def upload_file(self, uploadlocalfilepath, uploadremotefilepath):
#     "This method uploads the file to remote server"
#     result_flag = True
#     try:
#         if self.connect():
#             ftp_client = self.client.open_sftp()
#             ftp_client.put(uploadlocalfilepath, uploadremotefilepath)
#             ftp_client.close()
#             self.client.close()
#         else:
#             print("Could not establish SSH connection")
#             result_flag = False
#     except Exception as e:
#         print('\nUnable to upload the file to the remote server', uploadremotefilepath)
#         print('PYTHON SAYS:', e)
#         result_flag = False
#         ftp_client.close()
#         self.client.close()
#
#     return result_flag
