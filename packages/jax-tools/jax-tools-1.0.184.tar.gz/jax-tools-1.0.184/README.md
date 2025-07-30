# Jax Tools
Jax common tools

## Install
```shell
pip3 install jax-tools
```

update
```shell
pip3 install jax-tools --upgrade
```


## Usage

### Use network port detection

```shell
nd dest_ip dest_port
```

### Use logger

```python
from jax_tools.logger import logger
logger.info('info')
logger.debug('debug')
logger.warning('warning')
logger.error('error')
logger.critical('critical')
```
### Use ssh

```python
from jax_tools.ssh import SSHClient
ssh_client = SSHClient(host='dest_ip', port=22, username='username', password='password')
print(ssh_client.run_cmd('ls'))
```

