import hashlib
from . import Bank
from . import Client
from .ClientException import ClientException


class Admin :
    def __init__(self , name , password , homeBank , login_id) :
        self.__name = name
        self.__password = password
        self.__homeBank = homeBank
        self.__login_id = login_id

    def getAllClientsAsString(self) :
        my_database = Bank.Bank.createConnection ( )
        mycursor = my_database.cursor ( )

        try :
            mycursor.execute ( "SELECT * FROM Clients" )
            my_database.close ( )
        except Exception as exception :
            my_database.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        client_fields_array = mycursor.fetchall ( )
        clients_in_string_format = ""
        for client_fields in client_fields_array :
            client = Client.Client ( client_fields[0] , client_fields[1] , self , client_fields[2] , client_fields[3] ,
                                     client_fields[4] , client_fields[5] )
            clients_in_string_format += client.__str__ ( ) + "\n"

        return clients_in_string_format

    def deleteClient(self , nameP , passwordP) :
        mydb = Bank.Bank.createConnection ( )
        passwordHashed = hashlib.md5 ( passwordP.encode ( "utf-8" ) )
        passwordHexa = passwordHashed.hexdigest ( )

        mycursor = mydb.cursor ( )
        try :
            result = mycursor.execute ( "DELETE FROM Clients WHERE name = %s AND password = %s" ,
                                        (nameP , passwordHexa) )
            mydb.commit ( )

            result = mycursor.rowcount
            if result == 0 :
                raise ClientException ( 'The client is not present in our database' )

        except ClientException as e :
            mydb.close ( )
            raise e

        except Exception as e:
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )
        finally :
            mydb.close ( )

    def __passwordExistInDatabase(self , mydb , password_introduced) :
        mycursor = mydb.cursor ( )
        mycursor.execute ( "SELECT password FROM Admins" )

        myresult = mycursor.fetchall ( )

        exist = 0
        for x in myresult :
            if x[0] == password_introduced :
                exist = 1
        return exist

    def createAdminAccount(self , name , password) :
        mydb = Bank.Bank.createConnection ( )
        if (self.__passwordExistInDatabase ( mydb , password ) == 1) :
            raise PasswordAlreadyExistsException.PasswordAlreadyExistsException ( )

        mycursor = mydb.cursor ( )

        try :
            mycursor.execute ( "INSERT INTO Admins (name, password) VALUES (%s, %s)" , (name , password) )
            mydb.commit ( )
        except BaseException as e :
            mydb.close ( )
            raise Exception ( "Something went wrong. Please try again later" )
        finally :
            mydb.close ( )

    def deposit_money_as_admin(self , money) :
        bank_sCredit = self.__homeBank.getTotalAmountOfMoney ( )
        bank_sCredit += money

        my_db_connection = Bank.Bank.createConnection ( )
        mycursor = my_db_connection.cursor ( )
        try :
            mycursor.execute ( "UPDATE bank SET moneyOwned = %s WHERE name='ING'" , (bank_sCredit) )
            my_db_connection.commit ( )

            result = mycursor.rowcount
            if result == 0 :
                raise Exception ( 'Unable to finish the update' )
            my_db_connection.close ( )
        except BaseException as e :
            my_db_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def __str__(self) :
        return "({0},{1})".format ( self.__name , self.__password )

    def get_login_id(self) :
        return self.__login_id

    def block_client_account_after_the_login_id(self , login_id) :
        if Bank.Bank.is_blocked_the_account_with_id ( login_id ) :
            raise ClientException ( "The account is already blocked" )

        database_connection = Bank.Bank.createConnection ( )

        my_cursor = database_connection.cursor ( )

        try :
            my_cursor.execute ( "UPDATE Clients SET blocked = %s WHERE login_id=%s" , (True , login_id) )
            database_connection.commit ( )

            result = my_cursor.rowcount
            if result == 0 :
                raise ClientException ( 'Unable to block the account' )
            database_connection.close ( )
        except ClientException as exception:
            database_connection.close()
            raise exception

        except BaseException as e :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    def unblock_client_account_after_the_login_id(self , login_id) :
        if not Bank.Bank.is_blocked_the_account_with_id ( login_id ) :
            raise ClientException ( "The account is already unblocked" )

        database_connection = Bank.Bank.createConnection ( )

        my_cursor = database_connection.cursor ( )

        try :
            my_cursor.execute ( "UPDATE Clients SET blocked = %s WHERE login_id=%s" , (False , login_id) )
            database_connection.commit ( )

            result = my_cursor.rowcount
            if result == 0 :
                raise Exception ( 'Unable to unblock the account' )
            database_connection.close ( )

        except ClientException as ex:
            database_connection.close()
            raise ex
        except BaseException as e :
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )
