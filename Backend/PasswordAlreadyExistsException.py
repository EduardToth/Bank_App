class PasswordAlreadyExistsException(Exception):
    def __init__(self, message="The password already exists in database"):
        self.__message = message

    def __str__(self):
        return self.__message
