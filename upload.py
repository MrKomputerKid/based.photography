import paramiko
import sys

def upload_via_ssh(file_path):
    host = 'your_ssh_host'
    port = 22
    username = 'your_ssh_username'
    private_key_path = '/path/to/your/private/key'  # Replace with the path to your private key
    remote_path = '/path/to/server/uploads/'

    # Load the private key
    private_key = paramiko.RSAKey(filename=private_key_path)

    # Establish an SSH connection using the private key
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, pkey=private_key)

    # Upload the file
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(file_path, remote_path + file_path)

    # Close the connection
    sftp.close()
    transport.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    upload_via_ssh(file_path)
    print(f"File {file_path} uploaded successfully.")

