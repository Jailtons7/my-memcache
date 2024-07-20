# MY-MEMCACHE
This project is my implementation of an in memory cache server using Python 
and the sockets library.

## RUNNING
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

## CLIENT
In this project we don't implemented a client, but you can use a telnet client
to connect to the server:

```shell
telnet 0.0.0.0 <int:port>
```

## SUPPORTED COMMANDS
The general command signature is:
```shell
<command_name> <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]
```

Follows the supported `<command_names>`

### set
To set data to the server use the set command.:
```shell
set <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]
# after enter
<data_block>
```


It will define a `key` in memory with the `data_block` as value. The server will respond with:
`STORED\r\n`.

It won't respond if `noreply` optional flag is passed in the command.
> Keep in mind that the parameters `flags`, `exptime` and `byte_count` must be integers.

### add
Similar to the set command, adds a new key if it doesn't exist
```shell
add <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]
# after enter
<data_block>
```
The server will respond with `STORED\r\n` if the key exists otherwise it will
respond with `NOT_STORED\r\n`.

### replace
This method replaces the value of an existing key
```shell
replace <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]
# after enter
<data_block>
```
The server will respond with `STORED\r\n` if the key exists otherwise it will
respond with `NOT_STORED\r\n`.

### append
This method change the value of an existing key adding new data at the end
```shell
append <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]
# after enter
<data_block>
```

### prepend
This method change the value of an existing key adding new data at the beginning
```shell
prepend <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]
# after enter
<data_block>
```

### get
Use the get command to get stored values.
```shell
get <str:key>
```
The server will respond with `END` if the key is not set
or if the key is `expired` otherwise the response will be
`VALUE <key> <flags> <byte_count>\r\n<block_data>`

## EXAMPLES
1. Starting the client connection
```shell
% telnet 0.0.0.0 11211
Trying ::1...
Connected to localhost.
Escape character is '^]'.
```

2. Testing the `set` and `get` commands
```shell
set test 0 0 4  # stores the key test with value 1234
1234
STORED
END
get test  # get the value stored for key 'test'
VALUE test 0 4
1234
END
set test2 1 0 7 noreply  # doesn't respond because of noreply
testing
END
get test2
VALUE test2 1 7
testing
END
```
3. Testing the expiration time

```shell
set test 0 1 4  # exptime 1 sec
test
STORED
END
get test  # not return it is expired
END
set test 0 100 4  # exptime 100 sec
test
STORED
END
get test  # returned
VALUE test 0 4
test
END
set test 0 -1 4  # negative exptime always expired 
test
STORED
END
get test
END
```

4. Testing `add` and `replace`
```shell
add test5 0 0 4  # stored because test5 doesn't exist
data
STORED
END
get test5
VALUE test 0 4
data
END
add test5 0 0 4  # not stored because test5 already exists
test
NOT_STORED
END
replace test5 0 0 4  # replaced because test5 already exist
john
STORED
END
get test  # return the new value
VALUE test 0 4
john
END
replace test3 0 0 4  # not stored because test3 doesn't exist
data
NOT_STORED
END
```
5. Testing `append` and `prepend`
```shell
add test 0 0 4
john
STORED
END
append test 0 0 4  # add at the end
more
STORED
END
get test
VALUE test 0 8  # see the updated byte_count
johnmore
END
prepend test 0 0 4  # add at the beginning
send
STORED
END
get test
VALUE test 0 12  # see the updated byte_count
sendjohnmore
END
append foo 0 0 4  # foo doesn't exist
test
NOT_STORED
END
prepend foo 0 0 4  # foo doesn't exist
test
NOT_STORED
END
```
