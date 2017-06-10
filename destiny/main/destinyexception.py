class DestinyException(Exception):
    def __init__(self, p_err_msg):
        self.err_message = p_err_msg

    def __str__(self):
        return self.err_message


class DestinyApiCallException(DestinyException):
    def __init__(self, p_err_code, p_err_msg):
        self.err_code = p_err_code
        self.err_message = p_err_msg

    def __str__(self):
        s = "Unexpected status code while calling the Riot-Games API: {} - {}".format(self.err_code, self.err_message)
        return s
