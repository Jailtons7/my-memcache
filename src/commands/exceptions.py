class CommandError(Exception):
    def __init__(
            self,
            message: str = "The command signature is\r\n"
                           "<str:command_name> <str:key> <int:flags> <int:exptime> <int:byte_count> [<str:noreply>]\r\n"
                           "Did you use int for flags, exptime and byte_count parameters?\r\n"
    ):
        self.message = message
        super().__init__(self.message)
