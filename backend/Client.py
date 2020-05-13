import datetime
import os

from dateutil.relativedelta import relativedelta

from . import Bank
import hashlib
from .encryption import crypt, decrypt
from .ClientException import ClientException
from .Debt import Debt


class Client:
    def __init__(self, userName, password, homeBank, depositedMoney, moneyBorrowed, login_id, is_blocked
                 , postal_code, phone_number, nationality, email, monthly_income):
        self.__userName = userName
        self.__password = password
        self.__homeBank = homeBank
        self.__depositedMoney = depositedMoney
        self.__moneyBorrowed = moneyBorrowed
        self.__login_id = login_id
        self.__is_blocked = is_blocked
        self.__debts = Debt.get_all_debts_with_person_id(self.__login_id)
        self.__postal_code = postal_code
        self.__phone_number = phone_number
        self.__nationality = nationality
        self.__email = email
        self.__monthly_income = monthly_income

    # merge
    def depositMoney(self, money):
        password_in_hexa = self.getPassword()

        self.__depositedMoney += money
        db_connection = None
        try:
            db_connection = Bank.Bank.createConnection()
            my_cursor = db_connection.cursor()

            if Bank.Bank.is_blocked_the_account_with_id(self.__login_id):
                raise ClientException("The account is blocked. Could not deposit money")

            my_cursor.execute("UPDATE Clients SET moneyOwned = %s WHERE name = %s AND password = %s",
                              (crypt(self.__depositedMoney), self.__userName, password_in_hexa))
            db_connection.commit()

            result = my_cursor.rowcount
            if result == 0:
                raise Exception('Unable to deposit the money')
            db_connection.close()
        except ClientException as e:
            db_connection.close()
            raise e
        except BaseException as e:
            db_connection.close()
            raise Exception("Something went wrong. Please try again later")

    # merge
    def withdrawMoney(self, moneyRequested):

        passwordHexa = self.getPassword()
        mydb = Bank.Bank.createConnection()

        if self.__depositedMoney < moneyRequested:
            raise ClientException('There is no enough money in your savings')

        self.__depositedMoney -= moneyRequested

        mycursor = mydb.cursor()
        try:
            if Bank.Bank.is_blocked_the_account_with_id(self.__login_id):
                raise ClientException("The account is blocked. Could not withdraw money")
            mycursor.execute("UPDATE Clients SET moneyOwned = %s WHERE name = %s AND password = %s",
                             (crypt(self.__depositedMoney), self.__userName, passwordHexa))
            mydb.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('Unable to finish the update')
            mydb.close()

        except ClientException as ex:
            mydb.close()
            raise ex
        except BaseException as e:
            mydb.close()
            raise Exception("Something went wrong. Please try again later")

    def __update_debt(self):

        mydb = Bank.Bank.createConnection()
        passwordHexa = self.getPassword()
        mycursor = mydb.cursor()

        try:
            mycursor.execute("UPDATE Clients SET debt = %s WHERE name = %s AND password = %s",
                             (crypt(self.__moneyBorrowed), self.__userName, passwordHexa))
            mydb.commit()
            mydb.close()
        except BaseException as e:
            mydb.close()
            raise Exception("Something went wrong. Please try again later")

    def get_credit_from_bank(self, money_requested, interest_rate, period_to_pay_in_months):
        if Bank.Bank.is_blocked_the_account_with_id(self.__login_id):
            raise ClientException("The account is blocked. You cannot get a credit")

        bank_s_credit = self.__homeBank.get_total_ammount_of_money()

        bank_s_credit -= money_requested
        database_connection = None
        try:
            today = datetime.date.today()

            debt = Debt.create_new_instance(money_requested,
                                            today + relativedelta(months=+period_to_pay_in_months),
                                            self.__login_id, interest_rate)
            debt.insert_to_database()
            database_connection = Bank.Bank.createConnection()
            my_cursor = database_connection.cursor()

            my_cursor.execute("UPDATE bank SET moneyOwned = %s WHERE name='ING'", crypt(bank_s_credit))
            database_connection.commit()

            self.__depositedMoney += money_requested
            self.__moneyBorrowed += money_requested
            my_cursor.execute("UPDATE Clients SET moneyOwned = %s WHERE password=%s",
                              (crypt(self.__depositedMoney), self.__password))
            database_connection.commit()

            self.__update_debt()
            database_connection.close()
        except BaseException as e:
            database_connection.close()
            raise Exception("Something went wrong. Please try again later")

    def is_debt_mine(self, debt_id):
        debt_list = Debt.get_all_debts_with_person_id(self.__login_id)
        my_debt = Debt.get_debt_with_id(debt_id)
        for debt in debt_list:
            if debt == my_debt:
                return True
        return False

    def pay_debt(self, id):
        if not self.is_debt_mine(id):
            raise ClientException('This debt id is not correct')

        debt = Debt.get_debt_with_id(id)
        if self.__depositedMoney < debt.get_money_to_pay_monthly():
            raise ClientException("You cannot pay this debt. You have not enough money")
        mydb = None

        bank_s_credit = self.__homeBank.get_total_ammount_of_money()
        try:
            mydb = Bank.Bank.createConnection()
            debt.pay_debt()
            bank_s_credit += debt.get_money_to_pay_monthly()
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE bank SET moneyOwned = %s WHERE name='ING'", crypt(bank_s_credit))
            mydb.commit()

            result = mycursor.rowcount
            if result == 0:
                raise Exception('Unable to pay the debt')
            self.__moneyBorrowed -= debt.get_money_to_pay_monthly()
            self.__update_debt()

            self.__depositedMoney -= debt.get_money_to_pay_monthly()
            mycursor.execute("UPDATE Clients SET moneyOwned = %s WHERE login_id=%s",
                             (crypt(self.__depositedMoney), self.__login_id))
            mydb.commit()
            mydb.close()
        except ClientException as exception:
            mydb.close()

            raise exception
        except BaseException as e:
            print(str(e))
            mydb.close()
            raise Exception("Something went wrong. Please try again later")

    def getUserName(self):
        return self.__userName

    def getPassword(self):
        return self.__password

    def getDepositedMoney(self):
        return self.__depositedMoney

    def getMoneyBorrowed(self):
        return self.__moneyBorrowed

    def __str__(self):
        text = ""
        text += "Name: " + self.__userName + os.linesep
        text += "Owned money: " + str(self.__depositedMoney) + os.linesep
        text += "Owed money: " + str(self.__moneyBorrowed) + os.linesep
        text += "Login id: " + str(self.__login_id) + os.linesep
        if self.__is_blocked:
            text += "The user is blocked" + os.linesep
        else:
            text += "The user is not blocked" + os.linesep
        if len(self.__debts) == 0:
            text += 'The client has no debts' + os.linesep
        else:
            text += "Debts: " + os.linesep
            for debt in self.__debts:
                text += str(debt) + os.linesep
        return text

    def get_login_id(self):
        return self.__login_id

    def is_blocked(self):
        return self.__is_blocked

    def set_log_field(self, is_logged):
        database_connection = Bank.Bank.createConnection()
        my_cursor = database_connection.cursor()

        try:
            my_cursor.execute("UPDATE Clients SET is_logged = %s WHERE login_id=%s", (is_logged, self.__login_id))
            database_connection.commit()

            database_connection.close()

        except BaseException as e:
            database_connection.close()
            raise Exception("Something went wrong. Please try again later")

    @staticmethod
    def create_instance(bank, parameter_list):
        userName = parameter_list[0]
        password = parameter_list[1]
        homeBank = bank
        depositedMoney = decrypt(parameter_list[2])
        moneyBorrowed = decrypt(parameter_list[3])
        login_id = parameter_list[4]
        is_blocked = parameter_list[5]
        postal_code = parameter_list[7]
        phone_number = parameter_list[8]
        nationality = parameter_list[9]
        email = parameter_list[10]
        monthly_income = decrypt(parameter_list[11])

        return Client(userName, password, homeBank, depositedMoney, moneyBorrowed, login_id,
                      is_blocked, postal_code, phone_number,
                      nationality, email, monthly_income)

    def insert_data_to_database(self):
        database_connection = None
        try:
            database_connection = Bank.Bank.createConnection()
            my_cursor = database_connection.cursor()
            my_cursor.execute("INSERT INTO Clients (name , password,"
                              " moneyOwned , debt , login_id , blocked, is_logged,"
                              " postal_code, phone_number, nationality, email, monthly_income)"
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                              (self.__userName,
                               self.__password,
                               crypt(self.__depositedMoney),
                               crypt(self.__moneyBorrowed),
                               self.__login_id,
                               self.__is_blocked,
                               0,
                               self.__postal_code,
                               self.__phone_number,
                               self.__nationality,
                               self.__email,
                               crypt(int(self.__monthly_income))))

            database_connection.commit()
            database_connection.close()
        except BaseException as exception:
            database_connection.close()
            raise Exception("Something went wrong. Please try again later: ")

    def get_monthly_income(self):
        return self.__monthly_income

    def get_monthly_debt_sum(self):
        sum = 0
        for debt in self.__debts:
            sum += debt.get_money_to_pay_monthly()

        return sum
