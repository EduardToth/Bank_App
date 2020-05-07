import os

from . import Bank
from .ClientException import ClientException


class Admin:
    def __init__(self, name, password, homeBank, login_id, email):
        self.__name = name
        self.__password = password
        self.__homeBank = homeBank
        self.__login_id = login_id
        self.__email = email

    def get_all_clients_as_string(self):
        my_database = Bank.Bank.createConnection()
        my_cursor = my_database.cursor()

        try:
            my_cursor.execute("SELECT login_id FROM Clients")
            my_database.close()
        except Exception as exception:
            my_database.close()
            raise Exception("Something went wrong. Please try again later")

        client_fields_array = my_cursor.fetchall()
        clients_in_string_format = ""
        for client_info in client_fields_array:
            client = Bank.Bank.get_client_after_the_login_id(client_info[0])
            clients_in_string_format += str(client) + os.linesep

        return clients_in_string_format

    def __password_exist_in_database(self, mydb, password_introduced):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT password FROM Admins")

        myresult = mycursor.fetchall()

        exist = False
        for x in myresult:
            if x[0] == password_introduced:
                exist = True
        return exist

    def create_admin_account(self, name, password):
        mydb = Bank.Bank.createConnection()
        if self.__password_exist_in_database(mydb, password) == 1:
            raise ClientException("The client already exist in database")

        mycursor = mydb.cursor()

        try:
            mycursor.execute("INSERT INTO Admins (name, password) VALUES (%s, %s)", (name, password))
            mydb.commit()
        except BaseException as e:
            mydb.close()
            raise Exception("Something went wrong. Please try again later")
        finally:
            mydb.close()

    def deposit_money_as_admin(self, money):
        bank_sCredit = self.__homeBank.get_total_ammount_of_money()
        bank_sCredit += money

        my_db_connection = Bank.Bank.createConnection()
        mycursor = my_db_connection.cursor()
        try:
            mycursor.execute("UPDATE bank SET moneyOwned = %s WHERE name='ING'", (bank_sCredit))
            my_db_connection.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('Unable to finish the update')
            my_db_connection.close()
        except BaseException as e:
            my_db_connection.close()
            raise Exception("Something went wrong. Please try again later")

    def __str__(self):
        return "({0},{1})".format(self.__name, self.__password)

    def get_login_id(self):
        return self.__login_id

    def block_client_account_after_the_login_id(self, login_id):
        if Bank.Bank.is_blocked_the_account_with_id(login_id):
            raise ClientException("The account is already blocked")

        database_connection = Bank.Bank.createConnection()

        my_cursor = database_connection.cursor()

        try:
            my_cursor.execute("UPDATE Clients SET blocked = %s WHERE login_id=%s", (True, login_id))
            database_connection.commit()

            result = my_cursor.rowcount
            if result == 0:
                raise ClientException('Unable to block the account')
            database_connection.close()
        except ClientException as exception:
            database_connection.close()
            raise exception

        except BaseException as e:
            database_connection.close()
            raise Exception("Something went wrong. Please try again later")

    def unblock_client_account_after_the_login_id(self, login_id):
        if not Bank.Bank.is_blocked_the_account_with_id(login_id):
            raise ClientException("The account is already unblocked")

        database_connection = Bank.Bank.createConnection()

        my_cursor = database_connection.cursor()

        try:
            my_cursor.execute("UPDATE Clients SET blocked = %s WHERE login_id=%s", (False, login_id))
            database_connection.commit()

            result = my_cursor.rowcount
            if result == 0:
                raise Exception('Unable to unblock the account')
            database_connection.close()

        except ClientException as ex:
            database_connection.close()
            raise ex

        except BaseException as e:
            database_connection.close()
            raise Exception("Something went wrong. Please try again later")

    def set_log_field(self, is_logged):
        database_connection = Bank.Bank.createConnection()
        my_cursor = database_connection.cursor()

        try:
            my_cursor.execute("UPDATE Admins SET is_logged = %s WHERE id=%s", (is_logged, self.__login_id))
            database_connection.commit()

            database_connection.close()

        except BaseException as e:
            database_connection.close()
            raise Exception("Something went wrong. Please try again later")

    @staticmethod
    def create_instance(parameter_list):
        name = parameter_list[0]
        password = parameter_list[1]
        homeBank = Bank.Bank('ING')
        login_id = parameter_list[2]
        email = parameter_list[4]

        return Admin(name, password, homeBank, login_id, email)
