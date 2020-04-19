import datetime
import os

from dateutil.relativedelta import relativedelta

from . import Bank
import hashlib

from .ClientException import ClientException
from .Debt import Debt


class Client :
    def __init__(self , userName , password , homeBank , depositedMoney , moneyBorrowed , login_id , is_blocked
                 , postal_code, phone_number, nationality, email, monthly_income, gender) :
        self.__userName = userName
        self.__password = password
        self.__homeBank = homeBank
        self.__depositedMoney = depositedMoney
        self.__moneyBorrowed = moneyBorrowed
        self.__login_id = login_id
        self.__is_blocked = is_blocked
        self.__debts = Debt.get_all_debts_with_person_id ( self.__login_id )
        self.__postal_code = postal_code
        self.__phone_number = phone_number
        self.__nationality = nationality
        self.__email = email
        self.__monthly_income = monthly_income
    # merge
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
        except ClientException as e :
            mydb.close ( )
            raise e
        except BaseException as e :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    # merge
    def withdrawMoney(self , moneyRequested) :

        passwordHexa = self.getPassword ( )
        mydb = Bank.Bank.createConnection ( )

        if (self.__depositedMoney < moneyRequested) :
            raise ClientException ( 'There is no enough money in your savings' )

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

        except ClientException as ex :
            mydb.close ( )
            raise ex
        except BaseException as e :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def __updateDebt(self) :

        mydb = Bank.Bank.createConnection()
        passwordHexa = self.getPassword ( )
        mycursor = mydb.cursor ( )

        try :
            mycursor.execute ( "UPDATE Clients SET debt = %s WHERE name = %s AND password = %s" ,
                               (self.__moneyBorrowed , self.__userName , passwordHexa) )
            mydb.commit ( )
            mydb.close()
        except BaseException as e :
            mydb.close()
            raise Exception ( "Something went wrong. Please try again later" )

    def getCreditFromBank(self , moneyRequested) :

        if Bank.Bank.is_blocked_the_account_with_id ( self.__login_id ) :
            raise ClientException ( "The account is blocked. You cannot get a credit" )
        bank_sCredit = self.__homeBank.getTotalAmountOfMoney ( )
        database_connection = Bank.Bank.createConnection ( )

        if bank_sCredit < moneyRequested :
            raise ClientException (
                'The bank does not have so much money' )

        bank_sCredit -= moneyRequested
        my_cursor = database_connection.cursor ( )

        try :
            my_cursor.execute ( "UPDATE bank SET moneyOwned = %s WHERE name='ING'" , bank_sCredit )
            database_connection.commit ( )
            self.__moneyBorrowed += moneyRequested
            self.__depositedMoney += moneyRequested
            self.__updateDebt ( )
            my_cursor.execute ( "UPDATE Clients SET moneyOwned = %s WHERE password=%s" ,
                                (self.__depositedMoney , self.__password) )
            database_connection.commit ( )
            database_connection.close ( )
        except BaseException as e :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def get_credit_from_bank(self , money_requested , interest_rate , period_to_pay_in_months) :
        if Bank.Bank.is_blocked_the_account_with_id ( self.__login_id ) :
            raise ClientException ( "The account is blocked. You cannot get a credit" )

        bank_s_credit = self.__homeBank.getTotalAmountOfMoney()

        bank_s_credit -= money_requested
        database_connection = None
        try :
            today = datetime.date.today ( )

            debt = Debt.create_new_instance(money_requested, today + relativedelta ( months = +period_to_pay_in_months ),
                                            self.__login_id, interest_rate)

            database_connection = Bank.Bank.createConnection ( )
            my_cursor = database_connection.cursor ( )

            my_cursor.execute ( "UPDATE bank SET moneyOwned = %s WHERE name='ING'" , bank_s_credit )
            database_connection.commit ( )

            self.__depositedMoney += money_requested
            self.__moneyBorrowed += money_requested
            my_cursor.execute ( "UPDATE Clients SET moneyOwned = %s WHERE password=%s" ,
                                (self.__depositedMoney , self.__password) )
            database_connection.commit ( )

            self.__updateDebt ( )
            database_connection.close ( )
        except BaseException as e :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def payDebt(self , money) :

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney ( )

        mydb = Bank.Bank.createConnection ( )
        try :
            if self.__moneyBorrowed < money :
                money = self.__moneyBorrowed
                self.__updateDebt ( )

            bank_sCredit += money
            mycursor = mydb.cursor ( )
            mycursor.execute ( "UPDATE bank SET moneyOwned = %s WHERE name='ING'" , bank_sCredit )
            mydb.commit ( )

            result = mycursor.rowcount
            if result == 0 :
                raise Exception ( 'Unable to pay the debt' )
            self.__moneyBorrowed -= money
            self.__updateDebt ( )
            mydb.close ( )


        except BaseException as e :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

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
        text += "Name: " + self.__userName + os.linesep
        text += "Owned money: " + str ( self.__depositedMoney ) + os.linesep
        text += "Owed money: " + str ( self.__moneyBorrowed ) + os.linesep
        text += "Login id: " + str ( self.__login_id ) + os.linesep
        if self.__is_blocked :
            text += "The user is blocked" + os.linesep
        else :
            text += "The user is not blocked" + os.linesep
        text += "Debts: " + os.linesep

        for debt in self.__debts:
            text += str( debt ) + os.linesep
        return text

    def get_login_id(self) :
        return self.__login_id

    def is_blocked(self) :
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


    @staticmethod
    def create_instance(bank, parameter_list):
        userName = parameter_list[ 0 ]
        password = parameter_list[ 1 ]
        homeBank = bank
        depositedMoney = parameter_list[ 2 ]
        moneyBorrowed = parameter_list[ 3 ]
        login_id = parameter_list[ 4 ]
        is_blocked = parameter_list[ 5 ]
        postal_code = parameter_list[ 6 ]
        phone_number = parameter_list[ 7 ]
        nationality = parameter_list[ 8 ]
        email = parameter_list[ 9 ]
        monthly_income = parameter_list[ 10 ]

        return Client(userName, password, homeBank, depositedMoney, moneyBorrowed, login_id,
                      is_blocked, postal_code, phone_number,
                      nationality, email, monthly_income)


    def paid_all_debts_for_this_month(self):
        paid = True
        for debt in self.__debts:
            if debt.debt_was_paid_for_this_month():
                paid = False

        return paid


    def insert_data_to_database(self):
        database_connection = None
        try :
            database_connection = Bank.Bank.createConnection ( )
            my_cursor = database_connection.cursor ( )
            my_cursor.execute ( "INSERT INTO Clients (name , password,"
                                " moneyOwned , debt , login_id , blocked, is_logged,"
                                " postal_code, phone_number, nationality, email, monthly_income)"
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                ( self.__userName ,
                                  self.__password ,
                                  self.__depositedMoney ,
                                  self.__moneyBorrowed ,
                                  self.__login_id ,
                                  self.__is_blocked,
                                  0,
                                  self.__postal_code,
                                  self.__phone_number,
                                  self.__nationality,
                                  self.__email,
                                  self.__monthly_income))

            database_connection.commit ( )
            database_connection.close ( )
        except BaseException as exception :
            print ( str ( exception ) )
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

