import Bank
import MySQLdb

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
            clientsString = 'Username: ' + x['name'] + '\n'
            clientsString += 'Password: ' + x['password'] + '\n'
            clientsString += 'Deposited money: ' + x['moneyOwned'] + '\n'
            clientsString += 'Money borrowed: ' + x['debt'] + '\n'

        if (mydb.is_connected()):
            mycursor.close()
            mydb.close()
            print("MySQL connection is closed")

        return clientsString

    def addMoneyForBank(self,money):
        if( money < 0 ):
            raise Exception('There is no way to add a negative ammount of money')

        bank_sCredit = self.__homeBank.getTotalAmountOfMoney()
        bank_sCredit += money

        mydb = Bank.Bank.createConnection()
        mycursor = mydb.cursor()
        try:
            mycursor.execute("UPDATE bank SET `moneyOwned`=bank_sCredit WHERE name='ING'")
            mydb.commit()

            return 1
        except MySQLdb.Error as e:
            print(e)
            return 0
        except:
            print('Unknown exception')
            return 0
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")

    def deleteClient(self, name, password):
        mydb = Bank.Bank.createConnection()
        mycursor = mydb.cursor()
        try:
            mycursor.execute("DELETE FROM Clients WHERE name='name' AND password='password'")
            mydb.commit()

            return 1
        except MySQLdb.Error as e:
            print(e)
            return 0
        except:
            print('Unknown exception')
            return 0
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
                print("MySQL connection is closed")



