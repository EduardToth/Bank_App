class TooMuchMoneyRequestedException(Exception):
    def __init__(self, message = "The bank cannot give you so much money"):
        self.__message = message

    def __str__(self):
        return self.__message
