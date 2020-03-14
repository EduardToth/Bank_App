import mysql.connector
import hashlib
import MySQLdb
import Admin
import Client
import UnfoundAdminException
import UnfoundClientException
import PasswordAlreadyExistsException

class Bank:
    def __init__(self, name):
        self.__name = name

    def __passwordExistInDatabase(self, mydb, password_introduced, table_name):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT password FROM table_name")

        myresult = mycursor.fetchall()

        exist = 0
        for x in myresult:
            if x == password_introduced:
                exist = 1

        return exist

    @staticmethod
    def createConnection(self):
        try:
            mydb = mysql.connector.connect(
                serverName = "localhost",
                userName = "Illes",
                password = "MindenOk10",
                dbName = "Bank"
            )
            return mydb
        except MySQLdb.Error as e:
            print(e)
        except:
            print('Something happened in createConnection()')

    def getTotalAmountOfMoney(self):
         mydb = self.createConnection()
         mycursor = mydb.cursor()

         mycursor.execute("SELECT `moneyOwned` FROM bank WHERE name='ING'")
         myresult = mycursor.fetchall()

         totalAmountOfMoney = 0
         for x in myresult:
             totalAmountOfMoney = x['moneyOwned']
             break

         if mydb.is_connected():
             mycursor.close()
             mydb.close()
             print("MySQL connection is closed")

         return totalAmountOfMoney

    def createClientAccount(self, name, password, moneyAmmount):
        mydb = self.createConnection()
        password = hashlib.md5(password.encode())

        if( self.__passwordExistInDatabase(mydb, password, 'Clients') == 1 ):
            raise PasswordAlreadyExistsException.PasswordAlreadyExistsException()

        mycursor = mydb.cursor()

        try:
            mycursor.execute("INSERT INTO Clients (name, password, `moneyOwned`, debt) VALUES ('name', 'password', 'moneyAmmount', 0)")
            mydb.commit()
            print('New record created succesfully in user table')
        except MySQLdb.Error as e:
            print(e)
        except:
            print('Something happened in createClientAccount')
        finally:
            if (mydb.is_connected()):
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    def getClient(self, name, password):
        mydb = self.createConnection()
        password = hashlib.md5(password.encode())
        mycursor= mydb.cursor()

        mycursor.execute("SELECT * FROM Clients WHERE name='name' AND password='password'")

        myresult = mycursor.fetchall()

        client = None
        for x in myresult:
            client = Client.Client(x['name'], x['password'], self, x['moneyOwned'], x['debt'])
            break

        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")

        if client is None:
              raise UnfoundClientException.UnfoundClientException()
        else:
              return client

    def getAdmin(self, name, password):
        mydb = self.createConnection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Admins WHERE name='name' AND password='password'")

        myresult = mycursor.fetchall()

        admin = None
        for x in myresult:
            admin = Admin.Admin(x['name'], x['passsword'], self)
            break

        if mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")

        if admin is None:
            raise UnfoundAdminException.UnfoundAdminException()
        else:
            return admin
