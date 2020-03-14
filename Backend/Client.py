import Bank
import TooMuchMoneyRequestedException
import MySQLdb

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

        mydb = Bank.Bank.createConnection()
        mycursor = mydb.cursor()

        self.__depositedMoney = money

        try:
            mydb.execute("UPDATE Clients SET `moneyOwned`=self.depositedMoney WHERE name='self.userName' AND password='self.password'")
            mydb.commit()

            return 1
        except MySQLdb.Error as e:
            print(e)
            return 0
        except:
            print('Something happened in depositMoney()')
            return 0
        finally:
            if (mydb.is_connected()):
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    def withdrawMoney(self, moneyRequested):
        if( moneyRequested < 0 ):
            raise Exception('There is no way to withdraw a negative ammount of money')

        mydb = Bank.Bank.createConnection()

        if(self.__depositedMoney < moneyRequested):
            raise TooMuchMoneyRequestedException.TooMuchMoneyRequestedException('There is no enough money in your savings')

        self.__depositedMoney -= moneyRequested

        mycursor = mydb.cursor()
        try:
            mycursor.execute("UPDATE Clients SET `moneyOwned`=self.depositedMoney WHERE name='self.userName' AND password='self.password'")
            mydb.commit()

            return 1
        except MySQLdb.Error as e:
            print(e)
            return 0
        except:
            print('Something happened in withdrawMoney()')
            return 0
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    def __updateDept(self,mydb):
        mycursor = mydb.cursor()

        try:
            mycursor.execute("UPDATE Clients SET `debt`=self.moneyBorrowed WHERE name='self.userName' AND password='self.password'")
            mydb.commit()

            return 1
        except MySQLdb.Error as e:
            print(e)
            return 0
        except:
            print('Something happened in __updateDebt()')
            return 0

    def getCreditFromBank(self,moneyRequested):
        if( moneyRequested < 0 ):
            raise Exception('There is no way to withdraw a negative ammount of money')

        mydb = Bank.Bank.createConnection()

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney()

        if(bank_sCredit < moneyRequested):
            raise TooMuchMoneyRequestedException.TooMuchMoneyRequestedException('The bank does not have so much money')

        bank_sCredit -= moneyRequested

        mycursor = mydb.cursor()
        try:
            mycursor.execute("UPDATE bank SET `moneyOwned`=bank_sCredit WHERE name='ING'")
            mydb.commit()
            self.__moneyBorrowed += moneyRequested
            if(self.__updateDept(mydb) == 0):
                raise Exception("Something went wrong")
            return 1
        except MySQLdb.Error as e:
            print(e)
            return 0
        except:
            raise Exception("Something happened in getCreditFromBank()")
            return 0
        finally:
            if (mydb.is_connected()):
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    def payDebt(self, money):
        if( money < 0 ):
            raise Exception('There is no way to pay a negative ammount of money')

        mydb = Bank.Bank.createConnection(self)

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney()

        if( self.__moneyBorrowed < money ):
            money = self.__moneyBorrowed
            if( self.__updateDept(mydb) == 0 ):
                raise Exception('Could not update the debt of the client. Payment uncomplete')

        bank_sCredit += money
        mycursor = mydb.cursor()

        try:
            mycursor.execute("UPDATE bank SET `moneyOwned`=bank_sCredit WHERE name='ING'")
            mydb.commit()
            self.__moneyBorrowed -= money
            self.__updateDept(mydb)
        except MySQLdb.Error as e:
            print(e)
            raise Exception("Could not access the database")
        except:
            print('Something happened in payDebt()')
        finally:
            if(mydb.is_connected()):
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

        return money

    def getUserName(self):
        return self.__userName

    def getPassword(self):
        return self.__password

    def getDepositedMoney(self):
        return self.__depositedMoney

    def getMoneyBorrowed(self):
        return self.__moneyBorrowed