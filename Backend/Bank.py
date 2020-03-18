import hashlib
import pymysql
import Admin
import Client
import UnfoundAdminException
import UnfoundClientException
import PasswordAlreadyExistsException

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
            mycursor.execute("INSERT INTO Clients (name, password, moneyOwned, debt) VALUES (%s, %s, %s, %s)", (nameP, passwordHexa, moneyAmmountP, 0))
            mydb.commit()
            print('New record created succesfully in user table')
        except BaseException as e:
            print(e)
            print('Something happened in createClientAccount()')
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
            client = Client.Client(x[0], x[1], self, x[2], x[3])
            break

        mydb.close()

        if client is None:
              raise UnfoundClientException.UnfoundClientException()
        else:
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
