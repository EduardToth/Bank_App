import hashlib
import Bank
import PasswordAlreadyExistsException

class Admin:
    def __init__(self, name, password, homeBank):
        self.__name = name
        self.__password = password
        self.__homeBank = homeBank

    def getAllClientsAsString(self):
        mydb = Bank.Bank.createConnection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Clients")
        myresult = mycursor.fetchall()

        clientsString = ""

        for x in myresult:
            clientsString += 'Username: ' + x[0] + '\n'
            clientsString += 'Password: ' + x[1] + '\n'
            clientsString += 'Deposited money: ' + str(x[2]) + '\n'
            clientsString += 'Money borrowed: ' + str(x[3]) + '\n'
            clientsString += '\n'

        mydb.close()

        return clientsString

    def addMoneyForBank(self, money):
        if money < 0:
            raise Exception('There is no way to add a negative ammount of money')

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney()
        bank_sCredit += money

        mydb = Bank.Bank.createConnection()
        mycursor = mydb.cursor()
        try:
            mycursor.execute("UPDATE bank SET moneyOwned = %s WHERE name='ING'", (bank_sCredit))
            mydb.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('Unable to finish the update')
            else:
                print('The ammount of money was succesfully updated')
            return 1
        except BaseException as e:
            print(e)
            print('Something happened in addMoneyForBank()')
            return 0
        finally:
            mydb.close()

    def deleteClient(self, nameP, passwordP):
        mydb = Bank.Bank.createConnection()
        passwordHashed = hashlib.md5(passwordP.encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()

        mycursor = mydb.cursor()
        try:
            result = mycursor.execute("DELETE FROM Clients WHERE name = %s AND password = %s", (nameP, passwordHexa))
            mydb.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('The client is not present in our database')
            else:
                print('Record deleted successfully')
            return 1
        except BaseException as e:
            print(e)
            print('Something happened in deleteClient()')
            return 0
        finally:
            mydb.close()

    def __passwordExistInDatabase(self, mydb, password_introduced):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT password FROM Admins")

        myresult = mycursor.fetchall()

        exist = 0
        for x in myresult:
            if x[0] == password_introduced:
                exist = 1
        return exist

    def createAdminAccount(self, name, password):
        mydb = Bank.Bank.createConnection()
        if (self.__passwordExistInDatabase(mydb, password) == 1):
            raise PasswordAlreadyExistsException.PasswordAlreadyExistsException()

        mycursor = mydb.cursor()

        try:
            mycursor.execute("INSERT INTO Admins (name, password) VALUES (%s, %s)",(name, password))
            mydb.commit()
            print('New record created succesfully in admin table')
        except BaseException as e:
            print(e)
            print('Something happened in createAdminAccount()')
        finally:
            mydb.close()

    def __str__(self):
        return "({0},{1})".format(self.__name, self.__password)
