import datetime
import os
from dateutil.relativedelta import relativedelta
from . import Bank
from .ClientException import ClientException


class Debt :
    # merge
    @staticmethod
    def get_date_difference_in_months(ending_date , starting_date) :
        years = ending_date.year - starting_date.year
        months = ending_date.month - starting_date.month

        return months + years * 12

    def __init__(self , money_to_pay , starting_date , ending_date , person_id ,
                 is_debt_paid , rate_of_interest ,
                 last_payment , debt_id) :
        self.__money_to_pay = money_to_pay + money_to_pay * rate_of_interest / 100
        self.__starting_date = starting_date
        self.__ending_date = ending_date
        self.__person_id = person_id
        self.__is_debt_paid = is_debt_paid
        self.__rate_of_interest = rate_of_interest
        self.__last_payment = last_payment
        self.__debt_id = debt_id
        self.__money_to_pay_monthly = (money_to_pay * (100 + rate_of_interest) / 100) / \
                                      Debt.get_date_difference_in_months ( ending_date , starting_date )

    def get_money_to_pay_monthly(self) :
        return self.__money_to_pay_monthly

    # merge
    def insert_to_database(self) :
        database_connection = None
        try :
            database_connection = Bank.Bank.createConnection ( )
            my_cursor = database_connection.cursor ( )
            my_cursor.execute (
                "INSERT INTO Debts   (Money_to_pay, Starting_date,"
                " Ending_date, PersonID,"
                " Debt_paid,"
                " rate_of_interest, "
                "last_payment,"
                "debt_id)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" ,
                (self.__money_to_pay ,
                 self.__starting_date ,
                 self.__ending_date ,
                 self.__person_id ,
                 self.__is_debt_paid ,
                 self.__rate_of_interest ,
                 self.__last_payment ,
                 self.__debt_id ,
                 ) )

            database_connection.commit ( )
            database_connection.close ( )
        except BaseException as exception :
            print ( str ( exception ) )
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    # merge
    def update_to_database(self) :

        database_connection = None
        try :
            database_connection = Bank.Bank.createConnection ( )
            my_cursor = database_connection.cursor ( )
            my_cursor.execute (
                "UPDATE  Debts SET  Money_to_pay = %s,"
                " Debt_paid = %s,"
                "last_payment = %s"
                " WHERE  debt_id = %s" ,
                (self.__money_to_pay ,
                 self.__is_debt_paid ,
                 self.__last_payment ,
                 self.__debt_id) )

            database_connection.commit ( )
            database_connection.close ( )
        except BaseException as ex :
            print ( str ( ex ) )
            database_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

    # merge
    @staticmethod
    def get_instance(debt_parameter_tuple) :
        money_to_pay = debt_parameter_tuple[0]
        starting_date = debt_parameter_tuple[1]
        ending_date = debt_parameter_tuple[2]
        person_id = debt_parameter_tuple[3]
        is_debt_paid = debt_parameter_tuple[4]
        rate_of_interest = debt_parameter_tuple[5]
        last_payment = debt_parameter_tuple[6]
        debt_id = debt_parameter_tuple[7]

        return Debt ( money_to_pay , starting_date , ending_date ,
                      person_id ,
                      is_debt_paid , rate_of_interest , last_payment ,
                      debt_id )

    # merge
    @staticmethod
    def get_all_debts_with_person_id(person_id) :

        debt_list = list ( )

        db_connection = None
        try :
            db_connection = Bank.Bank.createConnection ( )
            my_cursor = db_connection.cursor ( )
            my_cursor.execute ( "SELECT * FROM Debts WHERE PersonID = %s" , person_id )
            db_connection.close ( )
            debt_list_info = my_cursor.fetchall ( )

            for debt_info_tuple in debt_list_info :
                debt = Debt.get_instance ( debt_info_tuple )
                debt_list.append ( debt )
            return debt_list
        except BaseException :
            raise BaseException ( "Something went wrong. Please try again later" )

    # merge
    @staticmethod
    def get_debt_with_id(debt_id) :
        db_connection = None
        try :
            db_connection = Bank.Bank.createConnection ( )
            my_cursor = db_connection.cursor ( )
            my_cursor.execute ( "SELECT * FROM Debts WHERE debt_id=%s" , debt_id )
            db_connection.close ( )

            debt_list_info = my_cursor.fetchall ( )

            for debt_info_tuple in debt_list_info :
                debt = Debt.get_instance ( debt_info_tuple )
                return debt

            return None
        except BaseException as exception :
            print ( str ( exception ) )
            db_connection.close ( )
            raise BaseException ( "Something went wrong. Please try again later" )

    # merge
    def pay_debt(self) :
        date_difference_in_months = self.get_date_difference_in_months (  datetime.date.today ( ), self.__last_payment )
        if date_difference_in_months == 0 :
            raise ClientException ( 'The debt has been paid for this month already' )

        self.__money_to_pay -= self.__money_to_pay_monthly
        date_difference_in_months = date_difference_in_months - 1

        self.__last_payment = datetime.date.today ( ) - relativedelta ( months = +date_difference_in_months )

        if self.__money_to_pay == 0 :
            self.__is_debt_paid = True
        self.update_to_database ( )

    # merge
    def __str__(self) :
        text = '     Money to pay: ' + str ( self.__money_to_pay ) + os.linesep
        text += '     Starting date: ' + str ( self.__starting_date ) + os.linesep
        text += '     Ending date: ' + str ( self.__ending_date ) + os.linesep
        text += ('     The debt is paid' + os.linesep) if self.__is_debt_paid else (
                '     The debt is not paid' + os.linesep)
        text += '     Rate of interest: ' + str ( self.__rate_of_interest ) + '%' + os.linesep
        text += '     Last payment: ' + str ( self.__last_payment ) + os.linesep
        text += '     Debt id: ' + str ( self.__debt_id ) + os.linesep
        text += '     Money to pay monthly: ' + str ( self.__money_to_pay_monthly ) + os.linesep

        if self.debt_was_paid_for_this_month ( ) :
            text += '     The debt was paid for this month'
        else :
            text += '     The debt has not been paid for ' +\
                    str ( Debt.get_date_difference_in_months( datetime.date.today(),
                                                              self.__last_payment)) + ' months'
        text += os.linesep

        return text

    # merge
    @staticmethod
    def get_last_debt_id() :
        db_connection = Bank.Bank.createConnection ( )
        my_cursor = db_connection.cursor ( )

        try :
            my_cursor.execute ( "SELECT debt_id FROM Debts" )
            db_connection.close ( )
        except BaseException as exception :
            db_connection.close ( )
            raise Exception ( "Something went wrong. Please try again later" )

        debt_id_list = my_cursor.fetchall ( )
        last_debt_id = 0
        for debt_id in reversed ( debt_id_list ) :
            if debt_id[0] > last_debt_id :
                last_debt_id = debt_id[0]

        return last_debt_id

    # merge
    @staticmethod
    def create_new_instance(money_to_pay , ending_date , person_id , rate_of_interest) :
        today = datetime.date.today ( )
        debt = Debt ( money_to_pay , today , ending_date , person_id , False ,
                      rate_of_interest , today , Debt.get_last_debt_id ( ) + 1 )

        return debt

    def debt_was_paid_for_this_month(self) :
        date_difference_in_months = self.get_date_difference_in_months ( self.__last_payment , datetime.date.today ( ) )
        return date_difference_in_months == 0
