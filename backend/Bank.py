import hashlib
import pymysql
from . import Admin
from . import Client
from . import UnfoundAdminException
from . import UnfoundClientException
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
            print(e)
            print('Something happened in createConnection()')

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
        if( self.__passwordExistInDatabase(mydb, passwordHexa) == 1 ):
            raise PasswordAlreadyExistsException.PasswordAlreadyExistsException()

        mycursor = mydb.cursor()

        try:
            login_id = self.get_last_login_id() + 1
            is_blocked = False
            mycursor.execute("INSERT INTO Clients (name, password, moneyOwned, debt, login_id, blocked) VALUES (%s, %s, %s, %s, %s, %s)", (nameP, passwordHexa, moneyAmmountP, 0, login_id, is_blocked))
            mydb.commit()
            print('New record created succesfully in user table')
        except BaseException as e:
            raise e
        finally:
            mydb.close()

    def getClient(self, nameP, passwordP):
        passwordHashed = hashlib.md5(passwordP.encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()

        mydb = self.createConnection()
        mycursor= mydb.cursor()

        mycursor.execute("SELECT * FROM Clients WHERE name=%s AND password=%s", (nameP, passwordHexa))

        myresult = mycursor.fetchall()

        client = None
        for x in myresult:
            client = Client.Client(x[0], x[1], self, x[2], x[3], x[4], x[ 5 ])
            break

        mydb.close()

        if client is None:
            exception =  UnfoundClientException.UnfoundClientException()
            raise exception
        else:
            print(client.__str__())
            return client

    def getAdmin(self, nameP, passwordP):
        mydb = self.createConnection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Admins WHERE name=%s AND password=%s", (nameP, passwordP))

        myresult = mycursor.fetchall()

        admin = None
        for x in myresult:
            admin = Admin.Admin(x[0], x[1], self)
            break

        mydb.close()

        if admin is None:
            raise UnfoundAdminException.UnfoundAdminException()
        else:
            return admin

    def get_last_login_id(self):
        mydb = Bank.createConnection()
        mycursor = mydb.cursor()

        mycursor.execute ( "SELECT login_id FROM Clients" )
        mydb.close ( )
        login_ids = mycursor.fetchall ( )
        for x in reversed(login_ids):
            return x[ 0 ]

    @staticmethod
    def get_client_after_the_login_id(login_id):
        mydb = Bank.createConnection ( )
        mycursor = mydb.cursor ( )

        mycursor.execute ( "SELECT * FROM Clients WHERE login_id = %s", login_id )
        mydb.close ( )
        clients = mycursor.fetchall ( )
        for client in clients :
            client = Client.Client(client[ 0 ], client[ 1 ], Bank("ING"), client[ 2 ], client[ 3 ], client[ 4 ], client[ 5 ])
            return client


    @staticmethod
    def is_blocked_the_account_with_id(login_id):
        mydb = Bank.createConnection ( )
        mycursor = mydb.cursor ( )
        mycursor.execute ( "SELECT blocked FROM Clients WHERE login_id = %s" , login_id )

        mydb.close()

        blocked_values = mycursor.fetchall()

        return blocked_values[ 0 ][ 0 ]

    # def kell(self):
    #     nr = 0
    #     mydb = self.createConnection()
    #     mycursor = mydb.cursor()
    #     mycursor.execute("SELECT * FROM Clients")
    #     clients = mycursor.fetchall()
    #
    #     for client in clients:
    #         mycursor.execute ( "UPDATE Clients SET login_id = %s WHERE  password = %s",
    #                            (nr, client[ 1 ]) )
    #         nr = nr + 1
    #         mydb.commit()
    #     mydb.close()

