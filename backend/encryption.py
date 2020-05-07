import os
key = int(os.environ.get('SECRET_KEY'))
def crypt(number):
    return (number + key//2)^key

def decrypt(number):
    return (number^key) - key//2

