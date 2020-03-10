class UnfoundClientException(Exception):
    def __init__(self, message="This client account have not been created yet"):
        self.__message = message

    def __str__(self):
        return self.message
