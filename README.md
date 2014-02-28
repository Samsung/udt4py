udt4py
======

libudt4 Python wrapper written with Cython.

Tested with Python3 under Linux. In buffer operations bytes, bytearray and
memoryview objects are supported, allowing zero-copy operations.

In order to build the native module, execute:

```bash
python3 setup.py build_ext --inplace
```

In Ubuntu, you will need ``cython3`` package.
To run the tests, execute:

```bash
PYTHONPATH=`pwd` nosetests3 -w tests --tests socket,epoll
```

Example usage:

```python
from udt4py import UDTSocket


if __name__ == "__main__":
    socket = UDTSocket()
    socket.bind("0.0.0.0:7777")
    socket.listen()
    channel = socket.accept()
    msg = bytearray(5)
    channel.recv(msg)
```

Released under Simplified BSD License.
Copyright (c) 2014, Samsung Electronics Co.,Ltd.