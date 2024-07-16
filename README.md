# my-memcache
This project is my implementation of an in memory cache server using Python 
and the sockets library, since it uses type hints and asyncio module `Python >= 3.6`
is required.

## Running
This project has no third-party dependencies and hence to keep 
the server running just use
```shell
python main.py
```
it will start a server on default port: `11211`.

you can define the port as well:
```shell
python main.py -p <port>
```

## Client
In this project we don't implemented a client, but you can use a telnet client
to connect to the server:

```shell
telnet 0.0.0.0 <port>
```

## Supported Commands
### set
```shell
set <key> <flags> <exptime> <byte count> [<noreply>]
# after enter
<data-block>
```


It will define a `key` in memory with the `data-block` as value. The server will respond with:
```STORED\r\n```.

It won't respond if `noreply` optional flag is passed in the command.
> Keep in mind that the parameters `flags`, `exptime` and `byte_count` must be integers.
### get
```shell
get <key>
```
Use the get command to get stored values. The server will respond with `END` if the key is not set
otherwise the answer will be `VALUE <key> <flags> <byte_count>\r\n<block_data>`
