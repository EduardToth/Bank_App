from . import Bank
import hashlib

from .ClientException import ClientException


class Client :
    def __init__(self , userName , password , homeBank , depositedMoney , moneyBorrowed , login_id , is_blocked) :
        self.__userName = userName
        self.__password = password
        self.__homeBank = homeBank
        self.__depositedMoney = depositedMoney
        self.__moneyBorrowed = moneyBorrowed
        self.__login_id = login_id
        self.__is_blocked = is_blocked

    def depositMoney(self , money) :
        passwordHexa = self.getPassword ( )

        mydb = Bank.Bank.createConnection ( )
        mycursor = mydb.cursor ( )

        self.__depositedMoney += money

        print ( self.__depositedMoney )

        try :
            if Bank.Bank.is_blocked_the_account_with_id ( self.__login_id ) :
                raise ClientException ( "The account is blocked. Could not deposit money" )

            mycursor.execute ( "UPDATE Clients SET moneyOwned = %s WHERE name = %s AND password = %s" ,
                               (self.__depositedMoney , self.__userName , passwordHexa) )
            mydb.commit ( )

            result = mycursor.rowcount
            if result == 0 :
                raise Exception ( 'Unable to deposit the money' )
            mydb.close ( )
        except ClientException as e:
            mydb.close()
            raise e
        except BaseException as e :
            mydb.close ( )
            raise Exception("Something went wrong. Please try again later")

    def withdrawMoney(self , moneyRequested) :

        passwordHexa = self.getPassword ( )
        mydb = Bank.Bank.createConnection ( )

        if (self.__depositedMoney < moneyRequested) :
            raise ClientException('There is no enough money in your savings' )

        self.__depositedMoney -= moneyRequested

        mycursor = mydb.cursor ( )
        try :
            if Bank.Bank.is_blocked_the_account_with_id ( self.__login_id ) :
                raise ClientException ( "The account is blocked. Could not withdraw money" )
            mycursor.execute ( "UPDATE Clients SET moneyOwned = %s WHERE name = %s AND password = %s" ,
                               (self.__depositedMoney , self.__userName , passwordHexa) )
            mydb.commit ( )

            result = mycursor.rowcount
            if result == 0 :
                raise Exception ( 'Unable to finish the update' )
            mydb.close ( )

        except ClientException as ex:
            mydb.close()
            raise ex
        except BaseException as e :
            mydb.close ( )
            raise Exception("Something went wrong. Please try again later")

    def __updateDept(self , mydb) :
        passwordHexa = self.getPassword ( )
        mycursor = mydb.cursor ( )

        try :
            mycursor.execute ( "UPDATE Clients SET debt = %s WHERE name = %s AND password = %s" ,
                               (self.__moneyBorrowed , self.__userName , passwordHexa) )
            mydb.commit ( )
        except BaseException as e :
            raise Exception ( "Something went wrong. Please try again later" )

    def getCreditFromBank(self , moneyRequested) :

        if Bank.Bank.is_blocked_the_account_with_id ( self.__login_id ) :
            raise ClientException ( "The account is blocked. You cannot get a credit" )
        bank_sCredit = self.__homeBank.getTotalAmountOfMoney ( )
        database_connection = Bank.Bank.createConnection ( )

        if (bank_sCredit < moneyRequested) :
            raise ClientException (
                'The bank does not have so much money' )

        bank_sCredit -= moneyRequested
        my_cursor = database_connection.cursor ( )

        try :
            my_cursor.execute ( "UPDATE bank SET moneyOwned = %s WHERE name='ING'" , bank_sCredit )
            database_connection.commit ( )
            self.__moneyBorrowed += moneyRequested
            self.__depositedMoney += moneyRequested
            self.__updateDept ( database_connection )
            my_cursor.execute ( "UPDATE Clients SET moneyOwned = %s WHERE password=%s" ,
                               (self.__depositedMoney , self.__password) )
            database_connection.commit ( )
            database_connection.close ( )
        except BaseException as e :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def payDebt(self , money) :

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney ( )

        mydb = Bank.Bank.createConnection ( )
        try:
            if self.__moneyBorrowed < money :
                money = self.__moneyBorrowed
                self.__updateDept ( mydb )

            bank_sCredit += money
            mycursor = mydb.cursor ( )
            mycursor.execute ( "UPDATE bank SET moneyOwned = %s WHERE name='ING'" , bank_sCredit )
            mydb.commit ( )

            result = mycursor.rowcount
            if result == 0 :
                raise Exception ( 'Unable to pay the debt' )
            self.__moneyBorrowed -= money
            self.__updateDept ( mydb )
            mydb.close ( )


        except BaseException as e :
            mydb.close ( )
            raise Exception("Something went wrong. Please try again later")

        return money

    def getUserName(self) :
        return self.__userName

    def getPassword(self) :
        return self.__password

    def getDepositedMoney(self) :
        return self.__depositedMoney

    def getMoneyBorrowed(self) :
        return self.__moneyBorrowed

    def __str__(self) :
        text = ""
        text += "Name: " + self.__userName + "\n"
        text += "Owned money: " + str ( self.__depositedMoney ) + "\n"
        text += "Owed money: " + str ( self.__moneyBorrowed ) + "\n"
        text += "Login id: " + str ( self.__login_id ) + "\n"
        if self.__is_blocked:
            text += "The user is blocked\n"
        else :
            text += "The user is not blocked\n"

        return text

    def get_login_id(self) :
        return self.__login_id

    def is_blocked(self):
        return self.__is_blocked

    def set_log_field(self , is_logged) :
        database_connection = Bank.Bank.createConnection ( )
        my_cursor = database_connection.cursor ( )

        try :
            my_cursor.execute ( "UPDATE Clients SET is_logged = %s WHERE login_id=%s" , (is_logged , self.__login_id) )
            database_connection.commit ( )

            database_connection.close ( )

        except BaseException as e :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

