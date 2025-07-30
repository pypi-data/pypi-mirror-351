# sftppathlib

**sftppathlib** uses [**pathlib_abc**](https://pypi.org/project/pathlib-abc/) and [**paramiko**](https://pypi.org/project/paramiko/) to create a pathlib API for SFTP clients.

The documentation is the same as the standard [**pathlib**](https://docs.python.org/3/library/pathlib.html) library, with some differences.


## Differences

The methods **expanduser()**, **readlink()**, **hardlink_to**, **replace()**, **owner()**, **group()**, **from_uri**, **as_uri()** are not supported. Subsequently, any method in **pathlib_abc** which relies on these will also fail. For some of them, it's because they don't have any meaning on SFTP clients, others because I don't trust myself to implement them correctly.

The methods **stat**, **symlink_to**, **chmod** have their respective parameters **follow_symlinks**, **target_is_directory**, **follow_symlinks** ignored, since Paramiko's **SFTPClient** does not support them.

Some of Paramiko's **SFTPClient** methods would return status codes like `SFTP_OK`; these are ignored.


## Usage

The **sftppathlib** relies on an instance of an **SFTPClient** to be used. This can be either be created in the background using the default setup, or manually and passing it to the **\_\_init\_\_** constructor.


### With setup

The default connection will use Paramiko's **SSHClient** to connect. If you are only connecting to one SFTP server, it's recommended to create a config file in the application directory:

* Windows: `~/AppData/Roaming/sftppathlib/config.yaml`
* Linux: `~/.local/share/sftppathlib/config.yaml`
* Apple: `~/Library/Application Support/sftppathlib/config.yaml`

The file should be the parameters passed to [SSHClient.connect()](https://docs.paramiko.org/en/latest/api/client.html#paramiko.client.SSHClient.connect).

```yaml
hostname: sftp.<domain>
port: 22
username: <username>
password: <password>
```

It will also use the key defined in `~/.ssh/known_hosts`. This will typically include an entry starting with `[sftp.<domain>]:22`.

After this, **sftppathlib.SFTPPath** can be used like **pathlib.Path**:

```py
from sftppathlib import SFTPPath

root = SFTPPath("www/")
path = root / "hello.txt"

path.write_text("hello world", encoding="utf-8")
print(path.read_text(encoding="utf-8"))

for child in root.iterdir():
    print(child)
```


### Without setup

**Note**: The `CREDENTIALS` variable should be imported from another file or a module; never include secrets in code.

```py
import paramiko
from sftppathlib import SFTPPath

CREDENTIALS = {
    "hostname": "sftp.<domain>",
    "port": 22,
    "username": "<username>",
    "password": "<password>",
}

ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys()
ssh_client.connect(**CREDENTIALS)

sftp_client = paramiko.sftp_client.SFTPClient.from_transport(
    ssh_client.get_transport())


root = SFTPPath("www/", accessor=sftp_client)

...
```

If many instances are needed, it can be beneficial to subclass `SFTPClient` and create a `Path` method:

```py
...

class SFTPPathClient(paramiko.sftp_client.SFTPClient):
    def Path(self, path, *paths):
        return SFTPPath(path, *paths, accessor=self)


sftp_path_client = SFTPPathClient.from_transport(
    ssh_client.get_transport())


root = sftp_path_client.SFTPPath("www/")

...
```


### Closing connections

It is assumed that you want to keep the connections open during the duration of the program. If not, please use `SFTPClient.close()` and `SSHClient.close()`.


## Acknowledgments

Thanks to the [paramiko/contributors](https://github.com/paramiko/paramiko/graphs/contributors) and the [pathlib-abc/contributors](https://github.com/barneygale/pathlib-abc). This extends to anyone involved with the standard **pathlib** library, but I cannot find the list.
