import hashlib
import sys
from dateutil.relativedelta import relativedelta

from backend.Bank import Bank
from backend.ClientException import ClientException
from backend.Debt import Debt


def deleteDebtsWithId(id):
    mydb = Bank.createConnection ( )

    mycursor = mydb.cursor ( )
    try :
        result = mycursor.execute ( "DELETE FROM Debts WHERE PersonID = %s" ,
                                    (id,) )
        mydb.commit ( )

        result = mycursor.rowcount
        if result == 0 :
            raise ClientException ( 'Failed_to_delete' )

    except ClientException as e :
        mydb.close ( )
        raise e

    except Exception as e :
        mydb.close ( )
        raise Exception ( "Something went wrong. Please try again later" )
    finally :
        mydb.close ( )

def deleteClient(nameP , passwordP) :
    mydb = Bank.createConnection ( )
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

    except Exception as e :
        mydb.close ( )
        raise Exception ( "Something went wrong. Please try again later" )
    finally :
        mydb.close ( )


def debt_limit_test():
    bank = Bank ( "ING" )

    bank.createClientAccount ( 'Fictiv' , 'fictiv_password' , '3030046' , '0752187733' , 'German' ,
                               'fictiv@gmail.com' , 900 )

    client = bank.getClient ( 'Fictiv' , 'fictiv_password' )
    count = 0
    try :
        if Bank.is_safe_to_give_the_credit(client.get_login_id(), 200, 1):
            client.get_credit_from_bank ( 200 , 0 , 1 )
        else:
            raise ClientException("It did not work")
        count = count + 1
    except BaseException as exception :
        print ( str ( exception ) )

    try :
        if Bank.is_safe_to_give_the_credit ( client.get_login_id ( ) , 50 , 1 ) :
            client.get_credit_from_bank ( 200 , 0 , 1 )
        else :
            raise ClientException ( "It did not work" )
        count = count + 1
    except BaseException as exception :
        print ( str ( exception ) )

    try :
        if Bank.is_safe_to_give_the_credit ( client.get_login_id ( ) , 500 , 4 ) :
            client.get_credit_from_bank ( 200 , 0 , 1 )
        else :
            raise ClientException ( "It did not work" )
    except BaseException as exception :
        count = count + 1

    deleteDebtsWithId( client.get_login_id())
    deleteClient('Fictiv', 'fictiv_password')

    if count is 3:
        print('The debt limit test passed')
    else:
        print('The debt limit test failed')


def full_payment_test():
    bank = Bank ( 'ING')

    bank.createClientAccount ( 'Fictiv' , 'fictiv_password' , '3030046' , '0752187733' , 'German' ,
                               'fictiv@gmail.com' , 900 )
    client = bank.getClient ( 'Fictiv' , 'fictiv_password' )

    try:
        Bank.is_safe_to_give_the_credit(client.get_login_id(), 100, 1)
        client.get_credit_from_bank(200, 5, 1)
    except BaseException as exception:
        print( str( exception ) )

    debts = Debt.get_all_debts_with_person_id( client.get_login_id())
    debt = debts[ 0 ]

    debt.__starting_date = debt.__starting_date - relativedelta(months = +1)
    debt.__ending_date = debt.__ending_date - relativedelta(months = +1)
    debt.__last_payment = debt.__last_payment - relativedelta(months = +1)

    debt.insert_to_database()

    print( str( client ) )
    client.pay_debt( debt.__debt_id)

    print( str(client ))

    if debt.__is_debt_paid:
        print('Full payment test passed')
    else:
        print('Full payment test failed')
    sys.stdin.read ( 1 )
    deleteDebtsWithId ( client.get_login_id ( ) )
    deleteClient ( 'Fictiv' , 'fictiv_password' )


debt_limit_test()
# full_payment_test()
