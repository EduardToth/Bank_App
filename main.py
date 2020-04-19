import flask
from flask import Flask , render_template , request
from backend.Bank import Bank
from backend.ClientException import ClientException

app = Flask ( __name__ )


def render_success_template(success_message) :
    return render_template ('successTemplate.html', success_message = success_message)


def render_failure_template(error_message) :
    return render_template ('failureTemplate.html', error_message = error_message)


def handle_client_register_request(bank) :
    name = request.form.get ( 'name' )
    password = request.form.get ( 'password' )
    postal_code = request.form.get('address')
    phone_number = request.form.get('phone')
    nationality = request.form.get('nationality')
    email = request.form.get('email')
    monthly_income = request.form.get('Monthly income')

    try :
        bank.createClientAccount(name, password, postal_code, phone_number, nationality, email, monthly_income)
        return render_success_template ( "Account created successfully" )
    except Exception as ex :
        return render_failure_template ( str( ex ) )


def handle_client_login_request(bank) :
    name = request.form.get ( 'name' )
    password = request.form.get ( 'password' )
    try :
        client = bank.getClient ( name , password )
        client.set_log_field ( True )
        return get_client_template ( client )
    except Exception as ex :
        return render_failure_template( str( ex ) )


def handle_admin_login_request(bank) :
    name = request.form.get ( 'name' )
    password = request.form.get ( 'password' )
    try :
        admin = bank.getAdmin ( name , password )
        admin.set_log_field ( True )
        return get_admin_template ( admin , bank )
    except BaseException as exception :
        return render_failure_template( str( exception ) )


def get_admin_template(admin , bank) :
    money_ammount = bank.getTotalAmountOfMoney ( )
    nr_of_clients = bank.get_nr_of_clients ( )
    clients_in_string_format = admin.getAllClientsAsString ( )
    login_id = admin.get_login_id ( )
    return render_template ('admin.html',
                            login_id = login_id,
                            money_ammount = money_ammount,
                            nr_of_clients = nr_of_clients,
                            clients_in_string_format = clients_in_string_format)


def handle_deposit_money_as_client() :
    money_to_deposit = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )
    client = Bank.get_client_after_the_login_id ( login_id )

    try :
        client.depositMoney ( money_to_deposit )
        return render_success_template ( "Money deposited successfully" )
    except BaseException as ex :
        return render_failure_template( ex.__str__ ( ) )


def handle_withdraw_money_as_client() :
    money_to_withdraw = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )
    client = Bank.get_client_after_the_login_id ( login_id )

    try :
        client.withdrawMoney ( money_to_withdraw )
        return render_success_template ( "Money withdrew successfully" )
    except BaseException as ex :
        return render_failure_template( ex.__str__ ( ) )


def handle_get_credit_request() :
    money = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )
    client = Bank.get_client_after_the_login_id ( login_id )

    try :
        client.getCreditFromBank ( money )
        return render_success_template("You have got the credit")
    except BaseException as ex :
        return render_failure_template( ex.__str__ ( ) )


def handle_pay_debt_request() :
    money = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )
    client = Bank.get_client_after_the_login_id ( login_id )

    try :
        client.payDebt ( money )
        return render_success_template( "Debt paid successfully" )
    except BaseException as ex :
        return render_failure_template( ex.__str__ ( ) )


def handle_deposit_money_as_admin(bank) :
    money = int ( request.form.get ( "money" ) )
    login_id = int ( request.form.get ( "login_id" ) )

    try :
        admin = bank.get_admin_after_the_login_id ( login_id )
        admin.deposit_money_as_admin ( money )
        return render_success_template( "Money deposited successfully" )
    except BaseException as exception :
        return render_failure_template( exception.__str__ ( ) )


def handle_block_client_account_request(bank) :
    client_s_login_id = int ( request.form.get ( "client-login-id" ) )
    login_id_of_the_current_admin = int ( request.form.get ( "login_id" ) )
    try :
        admin = bank.get_admin_after_the_login_id ( login_id_of_the_current_admin )
        admin.block_client_account_after_the_login_id ( client_s_login_id )
        return render_success_template( "The client account was blocked" )
    except BaseException as exception :
        return render_failure_template( exception.__str__ ( ) )


def handle_unblock_client_account_request(bank) :
    client_s_login_id = int ( request.form.get ( "client-login-id" ) )
    login_id_of_the_current_admin = int ( request.form.get ( "login_id" ) )
    try :
        admin = bank.get_admin_after_the_login_id ( login_id_of_the_current_admin )
        admin.unblock_client_account_after_the_login_id ( client_s_login_id )
        return render_success_template( "The client account was unblocked" )
    except BaseException as exception :
        return render_failure_template( exception.__str__ ( ) )


def reload_client_page(bank) :
    login_id = request.args.get ( 'id' )
    is_logged = bank.is_client_logged ( login_id )
    if is_logged :
        client = bank.get_client_after_the_login_id ( login_id )
        return get_client_template ( client )
    raise ClientException ( "You are not logged in as a client. Please login first" )


def reload_admin_page(bank) :
    login_id = request.args.get ( 'id' )
    is_logged = bank.is_admin_logged ( login_id )
    if is_logged :
        admin = bank.get_client_after_the_login_id ( login_id )
        return get_admin_template ( admin )
    raise ClientException ( "You are not logged in as an admin. Please login first" )


def get_client_template(client) :
    message_for_general_information = "You have " + \
                                      str ( client.getDepositedMoney ( ) ) + " dollars in your account\n"
    message_for_general_information += "You have to pay: " + \
                                       str ( client.getMoneyBorrowed ( ) ) + " to the bank"
    return render_template ('client.html', client = client,
                            message_for_general_information = message_for_general_information,
                            login_id = client.get_login_id ( ))


@app.route ( '/client.html' , methods = ['POST' , 'GET'] )
def handle_client_request() :
    bank = Bank ( "ING" )
    if flask.request.method == 'POST' :
        if request.form.get ( 'post-type' ) == 'login' :
            return handle_client_login_request ( bank )
        elif request.form.get ( 'post-type' ) == 'register' :
            return handle_client_register_request ( bank )
        elif request.form.get ( 'post-type' ) == 'deposit' :
            return handle_deposit_money_as_client ( )
        elif request.form.get ( 'post-type' ) == 'withdraw' :
            return handle_withdraw_money_as_client ( )
        elif request.form.get ( 'post-type' ) == 'get_credit' :
            return handle_get_credit_request ( )
        elif request.form.get ( 'post-type' ) == 'pay_debt' :
            return handle_pay_debt_request ( )
        else :
            return render_failure_template('Something went wrong. Please try again later')
    else :
        try :
            return reload_client_page ( bank )
        except ClientException as exception :
            return render_failure_template( exception.__str__ ( ) )


@app.route ( '/admin.html' , methods = ['POST' , 'GET'] )
def handle_admin_request() :
    bank = Bank ( "ING" )
    if flask.request.method == 'POST' :
        if request.form.get ( 'post-type' ) == 'admin_login' :
            return handle_admin_login_request ( bank )
        elif request.form.get ( 'post-type' ) == 'deposit-money' :
            return handle_deposit_money_as_admin ( bank )
        elif request.form.get ( 'post-type' ) == 'block-client' :
            return handle_block_client_account_request ( bank )
        elif request.form.get ( 'post-type' ) == 'unblock-client' :
            return handle_unblock_client_account_request ( bank )

        return render_failure_template('Something went wrong. Please try again later')
    else :
        try :
            return reload_admin_page ( bank )
        except ClientException as exception :
            return render_failure_template( exception.__str__ ( ) )


@app.route ( '/home.html' )
def render_home_page_request() :
    bank = Bank ( "ING" )

    if request.args.get ( 'mode' ) == '1' :
        login_id = request.args.get ( 'id' )
        client = bank.get_client_after_the_login_id ( login_id )
        client.set_log_field ( False )
        return render_template ('home.html')
    elif request.args.get ( 'mode' ) == '2' :
        login_id = request.args.get ( 'id' )
        admin = bank.get_admin_after_the_login_id ( login_id )
        admin.set_log_field ( False )
    return render_template ('home.html')


if __name__ == '__main__' :
    app.run ( debug = True )
