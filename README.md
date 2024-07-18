# my-memcache
This project is my implementation of an in memory cache server using Python 
and the sockets library.

## Running
This project has no third-party dependencies, but since we use asyncio module
`Python >= 3.6` is required. 

To keep the server running just execute
```shell
python main.py
```
it will start a server on default port: `11211`.  You can define the port as well:
```shell
python main.py -p <int:port>
```

## Client
In this project we don't implemented a client, but you can use a telnet client
to connect to the server:

```shell
telnet 0.0.0.0 <int:port>
```

## Supported Commands
### set
To set data to the server use the set command passing the flowing parameters:
```shell
set <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]
# after enter
<data_block>
```


It will define a `key` in memory with the `data_block` as value. The server will respond with:
```STORED\r\n```.

It won't respond if `noreply` optional flag is passed in the command.
> Keep in mind that the parameters `flags`, `exptime` and `byte_count` must be integers.
### get
Use the get command to get stored values.
```shell
get <str:key>
```
The server will respond with `END` if the key is not set
or if the key is `expired` otherwise the response will be
`VALUE <key> <flags> <byte_count>\r\n<block_data>`
