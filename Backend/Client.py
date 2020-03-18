import Bank
import TooMuchMoneyRequestedException
import hashlib

class Client:
    def __init__(self, userName, password, homeBank, depositedMoney, moneyBorrowed):
        self.__userName = userName
        self.__password = password
        self.__homeBank = homeBank
        self.__depositedMoney = depositedMoney
        self.__moneyBorrowed = moneyBorrowed

    def depositMoney(self, money):
        if( money < 0 ):
            raise Exception('There is no way to deposit a negative ammount of money')

        passwordHashed = hashlib.md5(self.__password.encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()

        mydb = Bank.Bank.createConnection()
        mycursor = mydb.cursor()

        self.__depositedMoney += money

        try:
            mycursor.execute("UPDATE Clients SET moneyOwned = %s WHERE name = %s AND password = %s", (self.__depositedMoney, self.__userName, passwordHexa))
            mydb.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('Unable to deposit the money')
            else:
                print('The ammount of money was succesfully updated')
            return 1
        except BaseException as e:
            print(e)
            print('Something happened in depositMoney()')
            return 0
        finally:
                mydb.close()

    def withdrawMoney(self, moneyRequested):
        if( moneyRequested < 0 ):
            raise Exception('There is no way to withdraw a negative ammount of money')

        passwordHashed = hashlib.md5(self.__password.encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()

        mydb = Bank.Bank.createConnection()

        if(self.__depositedMoney < moneyRequested):
            raise TooMuchMoneyRequestedException.TooMuchMoneyRequestedException('There is no enough money in your savings')

        self.__depositedMoney -= moneyRequested

        mycursor = mydb.cursor()
        try:
            mycursor.execute("UPDATE Clients SET moneyOwned = %s WHERE name = %s AND password = %s", (self.__depositedMoney, self.__userName, passwordHexa))
            mydb.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('Unable to finish the update')
            else:
                print('The ammount of money was succesfully updated')
            return 1
        except BaseException as e:
            print(e)
            print('Something happened in withdrawMoney()')
            return 0
        finally:
            mydb.close()

    def __updateDept(self,mydb):
        passwordHashed = hashlib.md5(self.__password.encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()

        mycursor = mydb.cursor()

        try:
            mycursor.execute("UPDATE Clients SET debt = %s WHERE name = %s AND password = %s", (self.__moneyBorrowed, self.__userName, passwordHexa))
            mydb.commit()

            result = mycursor.rowcount
            return 1
        except BaseException as e:
            print(e)
            print('Something happened in __updateDebt()')
            return 0

    def getCreditFromBank(self,moneyRequested):
        if( moneyRequested < 0 ):
            raise Exception('There is no way to withdraw a negative ammount of money')

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney()

        mydb = Bank.Bank.createConnection()

        if(bank_sCredit < moneyRequested):
            raise TooMuchMoneyRequestedException.TooMuchMoneyRequestedException('The bank does not have so much money')

        bank_sCredit -= moneyRequested

        mycursor = mydb.cursor()
        try:
            mycursor.execute("UPDATE bank SET moneyOwned = %s WHERE name='ING'", bank_sCredit)
            mydb.commit()
            self.__moneyBorrowed += moneyRequested
            if(self.__updateDept(mydb) == 0):
                raise Exception("Something went wrong")
            return 1
        except BaseException as e:
            print(e)
            print('Something happened in getCreditFromBank()')
            return 0
        finally:
            mydb.close()

    def payDebt(self, money):
        if( money < 0 ):
            raise Exception('There is no way to pay a negative ammount of money')

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney()

        mydb = Bank.Bank.createConnection()

        if( self.__moneyBorrowed < money ):
            money = self.__moneyBorrowed
            if( self.__updateDept(mydb) == 0 ):
                raise Exception('Could not update the debt of the client. Payment uncomplete')

        bank_sCredit += money
        mycursor = mydb.cursor()

        try:
            mycursor.execute("UPDATE bank SET moneyOwned = %s WHERE name='ING'", bank_sCredit)
            mydb.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('Unable to pay the debt')
            else:
                print('Debt paid')
            self.__moneyBorrowed -= money
            self.__updateDept(mydb)
        except BaseException as e:
            print(e)
            print('Something happened in payDebt()')
            return 0
        finally:
            mydb.close()

        return money

    def getUserName(self):
        return self.__userName

    def getPassword(self):
        return self.__password

    def getDepositedMoney(self):
        return self.__depositedMoney

    def getMoneyBorrowed(self):
        return self.__moneyBorrowed

    def __str__(self):
        return "({0},{1})".format(self.__userName, self.__password)