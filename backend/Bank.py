import hashlib
from math import ceil

import pymysql
from . import Admin
from . import Client
from .ClientException import ClientException


class Bank :
    def __init__(self , name) :
        self.__name = name

    def __passwordExistInDatabase(self , mydb , password_introduced) :
        mycursor = mydb.cursor ( )

        try :
            mycursor.execute ( "SELECT password FROM Clients" )
        except BaseException as ex :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        myresult = mycursor.fetchall ( )

        exist = 0
        for x in myresult :
            if x[0] == password_introduced :
                exist = 1

        return exist

    @staticmethod
    def createConnection() :
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

    def createClientAccount(self ,  userName , password,
                            postal_code, phone_number, nationality, email, monthly_income) :
        passwordHashed = hashlib.md5 ( password.encode ( "utf-8" ) )
        passwordHexa = passwordHashed.hexdigest ( )
        login_id = self.get_last_login_id ( ) + 1
        client = Client.Client(userName, passwordHexa, self, 0, 0, login_id, False, postal_code, phone_number,
                               nationality, email, monthly_income)
        client.insert_data_to_database()

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
            client = Client.Client.create_instance(self, client_info)
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
        for admin_info in admin_infos :
            admin = Admin.Admin ( admin_info[0] , admin_info[1] , self , admin_info[2] )
            if admin is None :
                raise ClientException ( "The admin does not exists in our database" )
            return admin

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
            if last_login_id < login_id[ 0 ]:
                last_login_id = login_id[0]

        return last_login_id

    @staticmethod
    def get_client_after_the_login_id(login_id) :
        mydb = Bank.createConnection ( )
        mycursor = mydb.cursor ( )

        try :
            mycursor.execute ( "SELECT * FROM Clients WHERE login_id = %s" , login_id )
        except BaseException as exception :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )
        mydb.close ( )
        client_info = None
        client_infos = mycursor.fetchall ( )
        for client_info in client_infos :
            client_info = Client.Client ( client_info[0] , client_info[1] , Bank ( "ING" ) , client_info[2] ,
                                          client_info[3] , client_info[4] ,
                                          client_info[5] )
            break
        return client_info

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

        admin = None
        for admin_fields in admin_fields_array :
            admin = Admin.Admin (
                admin_fields[0] , admin_fields[1] , self , admin_fields[2] )

        return admin

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
            print ( exception.__str__ ( ) )
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
            print ( exception.__str__ ( ) )
            raise Exception ( "Something went wrong. Please try again later" )

    @staticmethod
    def is_safe_to_give_the_credit(monthly_income, money_requested, period_in_months):
        if monthly_income < 3 * money_requested / period_in_months :
            return False
        return True

    @staticmethod
    def get_offer(monthly_income, money_requested):
        money_to_pay_monthly = monthly_income / 3

        period_in_month = ceil( money_requested / money_to_pay_monthly)

        return period_in_month, money_to_pay_monthly
