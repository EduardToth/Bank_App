from flask import Flask , render_template , request
from backend.Bank import Bank , UnfoundClientException , PasswordAlreadyExistsException, Client

app = Flask ( __name__ )


def handle_client_register_request(bank) :
    name = request.form.get ( 'name' )
    password = request.form.get ( 'password' )
    try :
        bank.createClientAccount ( name , password , 0 )
        return "Account created successfully"
    except Exception  as ex :
        return ex.__str__ ( )


def handle_client_login_request(bank) :
    name = request.form.get ( 'name' )
    password = request.form.get ( 'password' )
    try :
        client = bank.getClient( name , password )
    except Exception as ex :
        return ex.__str__ ( )

    message_for_general_information = "You have " + str (client.getDepositedMoney ( ) ) + " dollars in your account\n"
    message_for_general_information += "You have to pay: " + str( client.getMoneyBorrowed())  + " to the bank"

    return render_template ( 'client.html' , client = client ,
                             message_for_general_information = message_for_general_information, login_id = client.login_id )


def handle_admin_login_request(bank) :
    name = request.form.get ( 'name' )
    password = request.form.get ( 'password' )
    # try :
    admin = bank.getAdmin ( name , password )
    money_ammount = bank.getTotalAmountOfMoney()
    nr_of_clients = 150
    return render_template ( 'admin.html', money_ammount = money_ammount, nr_of_clients = nr_of_clients)

def handle_deposit_money_as_client():

    money_to_deposit = int(request.form.get("money"))
    login_id = int(request.form.get("login_id"))
    client = Bank.get_client_after_the_login_id(login_id)

    try:
        client.depositMoney ( money_to_deposit )
        return "Money deposited successfully"
    except BaseException as ex:
        return ex.__str__()


def handle_withdraw_money_as_client():
    money_to_withdraw = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )
    client = Bank.get_client_after_the_login_id ( login_id )

    try:
        client.withdrawMoney( money_to_withdraw )
        return "Money withdrew successfully"
    except BaseException as ex:
        return ex.__str__()

def handle_get_credit_request():
    money = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )
    client = Bank.get_client_after_the_login_id ( login_id )

    try:
        client.getCreditFromBank( money )
        return "You have got the credit"
    except BaseException as ex:
        return ex.__str__()

def handle_pay_debt_request():
    money = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )
    client = Bank.get_client_after_the_login_id ( login_id )

    try:
        client.payDebt( money )
        return "Debt paid successfully"
    except BaseException as ex:
        return ex.__str__()

@app.route ( '/client' , methods = ['POST'] )
def handle_client_request() :
    bank = Bank ( "ING" )
    if request.form.get ( 'post-type' ) == 'login' :
        return handle_client_login_request ( bank )
    elif request.form.get ( 'post-type' ) == 'register' :
        return handle_client_register_request ( bank )
    elif request.form.get ( 'post-type' ) == 'deposit' :
        return handle_deposit_money_as_client()
    elif request.form.get ( 'post-type' ) == 'withdraw' :
        return handle_withdraw_money_as_client()
    elif request.form.get ( 'post-type' ) == 'get_credit' :
        return handle_get_credit_request()
    elif request.form.get ( 'post-type' ) == 'pay_debt' :
        return handle_get_credit_request()
    else:
        return 'Something went wrong'


@app.route ( '/admin', methods = ['POST'] )
def handle_admin_request() :
    bank = Bank ( "ING" )
    if request.form.get ( 'post-type' ) == 'admin_login' :
        return handle_admin_login_request ( bank)

    return 'Something went wrong'


@app.route ( '/' )
def get_value() :
    return render_template ( 'home.html' )


if __name__ == '__main__' :
    app.run ( debug = True )


