import hashlib
import pymysql
from . import Admin
from . import Client
from . import UnfoundAdminException
from . import PasswordAlreadyExistsException


class Bank:
    def __init__(self, name):
        self.__name = name

    def __passwordExistInDatabase(self, mydb, password_introduced):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT password FROM Clients")

        myresult = mycursor.fetchall()

        exist = 0
        for x in myresult:
            if x[0] == password_introduced:
                exist = 1

        return exist

    @staticmethod
    def createConnection():
        try:
            mydb = pymysql.connect("localhost", "Illes", "MindenOk10", "Bank")
            return mydb
        except BaseException as e:
            raise e

    def getTotalAmountOfMoney(self):
        mydb = Bank.createConnection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT moneyOwned FROM bank WHERE name='ING'")
        myresult = mycursor.fetchall()

        totalAmountOfMoney = 0
        for x in myresult:
            totalAmountOfMoney = x[0]
            break

        mydb.close()

        return totalAmountOfMoney

    def createClientAccount(self, nameP, passwordP, moneyAmmountP):
        passwordHashed = hashlib.md5(passwordP.encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()

        mydb = Bank.createConnection()
        if (self.__passwordExistInDatabase(mydb, passwordHexa) == 1):
            raise PasswordAlreadyExistsException.PasswordAlreadyExistsException()

        mycursor = mydb.cursor()

        try:
            login_id = self.get_last_login_id() + 1
            is_blocked = False
            mycursor.execute(
                "INSERT INTO Clients (name, password, moneyOwned, debt, login_id, blocked) VALUES (%s, %s, %s, %s, %s, %s)",
                (nameP, passwordHexa, moneyAmmountP, 0, login_id, is_blocked))
            mydb.commit()
            mydb.close()
        except BaseException as e:
            mydb.close()
            raise e

    def getClient(self, nameP, passwordP):
        passwordHashed = hashlib.md5(passwordP.encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()

        mydb = self.createConnection()
        mycursor = mydb.cursor()

        mycursor.execute(
            "SELECT * FROM Clients WHERE name=%s AND password=%s", (nameP, passwordHexa))

        myresult = mycursor.fetchall()
        mydb.close()

        for x in myresult:
            client = Client.Client(x[0], x[1], self, x[2], x[3], x[4], x[5])
            if client is None:
                raise Exception("Have not found the client")
            return client

        return Exception("Have not found the client")

    def getAdmin(self, nameP, passwordP):

        hashed_password = hashlib.md5(passwordP.encode("utf-8"))
        password_in_hexa = hashed_password.hexdigest()

        database_connection = self.createConnection()
        mycursor = database_connection.cursor()

        try:
            mycursor.execute("SELECT * FROM Admins WHERE name=%s AND password=%s",
                             (nameP, password_in_hexa))
        except BaseException as exception:
            raise exception

        my_result = mycursor.fetchall()

        database_connection.close()
        for x in my_result:
            admin = Admin.Admin(x[0], x[1], self, x[2])
            if admin is None:
                raise UnfoundAdminException.UnfoundAdminException()
            return admin

        return None

    def get_last_login_id(self):
        mydb = Bank.createConnection()
        mycursor = mydb.cursor()

        try:
            mycursor.execute("SELECT login_id FROM Clients")
            mydb.close()
        except BaseException as exception:
            mydb.close()
            raise exception

        login_ids = mycursor.fetchall()
        last_login_id = 0
        for x in reversed(login_ids):
            last_login_id = x[0]

        return last_login_id

    @staticmethod
    def get_client_after_the_login_id(login_id):
        mydb = Bank.createConnection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Clients WHERE login_id = %s", login_id)
        mydb.close()
        client = None
        clients = mycursor.fetchall()
        for client in clients:
            client = Client.Client(client[0], client[1], Bank("ING"), client[2], client[3], client[4],
                                   client[5])
            break
        return client

    @staticmethod
    def is_blocked_the_account_with_id(login_id):
        mydb = Bank.createConnection()
        mycursor = mydb.cursor()
        try:
            mycursor.execute(
                "SELECT blocked FROM Clients WHERE login_id = %s", login_id)
            mydb.close()
        except BaseException as exception:
            mydb.close()
            raise exception

        blocked_values = mycursor.fetchall()

        return blocked_values[0][0]

    def get_nr_of_clients(self):
        my_database = Bank.createConnection()
        my_cursor = my_database.cursor()

        try:
            my_cursor.execute("SELECT login_id FROM Clients")
            my_database.close()
        except BaseException as exception:
            my_database.close()
            raise exception

        login_ids = my_cursor.fetchall()
        # the number  of the clients of the bank. Each client has a login id
        return len(login_ids)

    def get_admin_after_the_login_id(self, login_id):
        mydb = Bank.createConnection()
        mycursor = mydb.cursor()
        try:
            mycursor.execute("SELECT * FROM Admins WHERE id = %s", login_id)
            mydb.close()
        except BaseException as exception:
            mydb.close()
            raise exception

        admin_fields_array = mycursor.fetchall()

        admin = None
        for admin_fields in admin_fields_array:
            admin = Admin.Admin(
                admin_fields[0], admin_fields[1], self, admin_fields[2])

        return admin
