class UnfoundAdminException(Exception):
    def __init__(self, message="This admin is not present in the database"):
        self.__message = message

    def __str__(self):
        return self.__message
