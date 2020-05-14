import os

key = None
try:
    key = int(os.environ.get("SECRET_KEY"))
except BaseException as exception:
    print(str(exception))
    key = 9152873


def crypt(number):
    return (int(number) + key // 2) ^ key


def decrypt(number):
    return (int(number) ^ key) - key // 2
