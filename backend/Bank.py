import hashlib
from math import ceil

import pymysql
from . import Admin
from . import Client
from .ClientException import ClientException


class Bank :
    def __init__(self , name) :
        self.__name = name

    def __passwordExistInDatabase(self ,  password_introduced) :
        db = Bank.createConnection()
        my_cursor = db.cursor ( )

        try :
            my_cursor.execute ( "SELECT password FROM Clients" )
        except BaseException as ex :
            db.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        myresult = my_cursor.fetchall ( )

        exist = False
        for x in myresult :
            if x[0] == password_introduced :
                exist = True
        db.close()
        return exist

    @staticmethod
    def createConnection() :
        mydb = None
        try :
            mydb = pymysql.connect ( "localhost" , "Illes" , "MindenOk10" , "Bank" )
            return mydb
        except BaseException as e :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def getTotalAmountOfMoney(self) :
        mydb = Bank.createConnection ( )
        mycursor = mydb.cursor ( )
        try :
            mycursor.execute ( "SELECT moneyOwned FROM bank WHERE name='ING'" )
        except BaseException as ex :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        myresult = mycursor.fetchall ( )

        totalAmountOfMoney = 0
        for x in myresult :
            totalAmountOfMoney = x[0]
            break

        mydb.close ( )

        return totalAmountOfMoney

    def createClientAccount(self , userName , password ,
                            postal_code , phone_number , nationality , email , monthly_income) :
        passwordHashed = hashlib.md5 ( password.encode ( "utf-8" ) )
        passwordHexa = passwordHashed.hexdigest ( )
        login_id = self.get_last_login_id ( ) + 1
        if self.__passwordExistInDatabase(passwordHexa):
            raise BaseException('Something went wrong. Please try again later')

        client = Client.Client ( userName , passwordHexa , self , 0 , 0 , login_id , False , postal_code ,
                                 phone_number ,
                                 nationality , email , monthly_income )
        client.insert_data_to_database ( )

    def getClient(self , nameP , passwordP) :
        passwordHashed = hashlib.md5 ( passwordP.encode ( "utf-8" ) )
        passwordHexa = passwordHashed.hexdigest ( )

        mydb = self.createConnection ( )
        mycursor = mydb.cursor ( )

        try :
            mycursor.execute (
                "SELECT * FROM Clients WHERE name=%s AND password=%s" , (nameP , passwordHexa) )
        except BaseException as exception :
            mydb.close ( )
            raise Exception ( "Something went wront. Please try again later" )

        client_infos = mycursor.fetchall ( )
        mydb.close ( )

        for client_info in client_infos :
            client = Client.Client.create_instance ( self , client_info )
            if client is None :
                raise ClientException ( "The client does not exist in our database" )
            return client
        raise ClientException ( "The client does not exist in our database" )

    def getAdmin(self , nameP , passwordP) :

        hashed_password = hashlib.md5 ( passwordP.encode ( "utf-8" ) )
        password_in_hexa = hashed_password.hexdigest ( )

        database_connection = self.createConnection ( )
        mycursor = database_connection.cursor ( )

        try :
            mycursor.execute ( "SELECT * FROM Admins WHERE name=%s AND password=%s" ,
                               (nameP , password_in_hexa) )
        except BaseException as exception :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        admin_infos = mycursor.fetchall ( )

        database_connection.close ( )
        if len( admin_infos) > 0:
            return Admin.Admin.create_instance( admin_infos[ 0 ])
        raise ClientException('The admin does not exist in database')

    def get_last_login_id(self) :
        mydb = Bank.createConnection ( )
        mycursor = mydb.cursor ( )

        try :
            mycursor.execute ( "SELECT login_id FROM Clients" )
            mydb.close ( )
        except BaseException as exception :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        login_ids = mycursor.fetchall ( )
        last_login_id = 0
        for login_id in reversed ( login_ids ) :
            if last_login_id < login_id[0] :
                last_login_id = login_id[0]

        return last_login_id

    @staticmethod
    def get_client_after_the_login_id(login_id) :
        db_connection = Bank.createConnection ( )
        my_cursor = db_connection.cursor ( )

        try :
            my_cursor.execute ( "SELECT * FROM Clients WHERE login_id = %s" , login_id )
        except BaseException as exception :
            db_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )
        db_connection.close ( )
        client_infos = my_cursor.fetchall ( )
        if len( client_infos ) > 0:
            return Client.Client.create_instance(Bank('ING'), client_infos[ 0 ])
        raise Exception ( "Something went wrong. Please try again later" )

    @staticmethod
    def is_blocked_the_account_with_id(login_id) :
        mydb = Bank.createConnection ( )
        mycursor = mydb.cursor ( )
        try :
            mycursor.execute (
                "SELECT blocked FROM Clients WHERE login_id = %s" , login_id )
            mydb.close ( )
        except BaseException as exception :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        blocked_values = mycursor.fetchall ( )

        return blocked_values[0][0]

    def get_nr_of_clients(self) :
        my_database = Bank.createConnection ( )
        my_cursor = my_database.cursor ( )

        try :
            my_cursor.execute ( "SELECT login_id FROM Clients" )
            my_database.close ( )
        except BaseException as exception :
            my_database.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        login_ids = my_cursor.fetchall ( )
        # the number  of the clients of the bank. Each client has a login id
        return len ( login_ids )

    def get_admin_after_the_login_id(self , login_id) :
        mydb = Bank.createConnection ( )
        mycursor = mydb.cursor ( )
        try :
            mycursor.execute ( "SELECT * FROM Admins WHERE id = %s" , login_id )
            mydb.close ( )
        except BaseException as exception :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        admin_fields_array = mycursor.fetchall ( )

        if len ( admin_fields_array ) > 0 :
            return Admin.Admin.create_instance ( admin_fields_array[0] )
        raise ClientException ( 'The admin does not exist in database' )

    def is_client_logged(self , login_id) :
        database_connection = Bank.createConnection ( )
        mycursor = database_connection.cursor ( )

        try :
            mycursor.execute ( "SELECT is_logged FROM Clients WHERE login_id = %s" , login_id )
            database_connection.close ( )
            is_logged_list = mycursor.fetchall ( )
            return is_logged_list[0][0]
        except BaseException as exception :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def is_admin_logged(self , login_id) :
        database_connection = Bank.createConnection ( )
        mycursor = database_connection.cursor ( )

        try :
            mycursor.execute ( "SELECT is_logged FROM Admins WHERE id = %s" , login_id )
            database_connection.close ( )
            is_logged_list = mycursor.fetchall ( )
            return is_logged_list[0][0]
        except BaseException as exception :
            database_connection.close ( )
            print ( str ( exception ) )
            raise Exception ( "Something went wrong. Please try again later" )


    @staticmethod
    def get_offer(login_id , money_requested) :
        client = Bank.get_client_after_the_login_id( login_id)
        sum = client.get_monthly_debt_sum()
        money_the_client_could_pay_monthly = client.get_monthly_income() / 3 - sum

        if money_the_client_could_pay_monthly <= 50:
            raise ClientException("The bank cannot give any credit to you")

        period_in_months = ceil ( money_requested / money_the_client_could_pay_monthly )
        return period_in_months , Bank.get_rate_of_interest ( period_in_months )

    @staticmethod
    def get_rate_of_interest(period_in_months) :
        rate_of_interest = 0
        if period_in_months <= 2 * 12 :
            rate_of_interest = 5
        elif period_in_months <= 5 * 12 :
            rate_of_interest = 10
        else :
            rate_of_interest = 20
        return rate_of_interest


    @staticmethod
    def is_safe_to_give_the_credit(login_id, money_requested, period_in_months):
        client = Bank.get_client_after_the_login_id( login_id )
        monthly_debt = client.get_monthly_debt_sum()

        the_money_the_client_could_pay = client.get_monthly_income() / 3 - monthly_debt

        if the_money_the_client_could_pay <= 50:
            raise ClientException("The bank can't give any credit to you. It's too risky")

        if money_requested / period_in_months <= the_money_the_client_could_pay:
            return True
        return False



