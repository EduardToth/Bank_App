import os

import flask

from flask import Flask, render_template, request
from backend.Bank import Bank
from backend.ClientException import ClientException

app = Flask(__name__)


def handle_create_admin_request(bank):
    name = request.form.get('admin-name')
    password = request.form.get('password')
    password_again = request.form.get('password_again')

    if not(password == password_again):
        return render_failure_template("The passwords introduced did not match")

    host_admin_login_id = int(request.form.get("login_id"))
    email = request.form.get('email')

    try:
        admin = bank.get_admin_after_the_login_id(host_admin_login_id)
        admin.create_admin_account(name, password, email)
        return render_success_template("Account created")
    except BaseException as exception:
        return render_failure_template(str(exception))


def render_success_template(success_message):
    return render_template('successTemplate.html', success_message=success_message)


def render_failure_template(error_message):
    return render_template('failureTemplate.html', error_message=error_message)


def handle_client_register_request(bank):
    name = request.form.get('name')
    password = request.form.get('password')
    password_again  = request.form.get('password_again')
    if not(password == password_again):
        return render_failure_template('The passwords introduced did not match')
    postal_code = request.form.get('address')
    phone_number = request.form.get('phone')
    nationality = request.form.get('nationality')
    email = request.form.get('email')
    monthly_income = request.form.get('Monthly income')

    try:
        bank.create_client_account(name, password, postal_code, phone_number, nationality, email,
                                   monthly_income)
        return render_success_template("Account created successfully")
    except Exception as ex:
        return render_failure_template(str(ex))


def handle_client_login_request(bank):
    name = request.form.get('name')
    password = request.form.get('password')
    try:
        client = bank.getClient(name, password)
        client.set_log_field(True)
        return get_client_template(client)
    except Exception as ex:

        return render_failure_template(str(ex))


def handle_admin_login_request(bank):
    name = request.form.get('name')
    password = request.form.get('password')
    try:
        admin = bank.getAdmin(name, password)
        admin.set_log_field(True)
        return get_admin_template(admin, bank)
    except BaseException as exception:
        return render_failure_template(str(exception))


def get_admin_template(admin, bank):
    money_ammount = bank.get_total_ammount_of_money()
    nr_of_clients = bank.get_nr_of_clients()
    clients_in_string_format = admin.get_all_clients_as_string()
    login_id = admin.get_login_id()
    return render_template('admin.html',
                           login_id=login_id,
                           money_ammount=money_ammount,
                           nr_of_clients=nr_of_clients,
                           clients_in_string_format=clients_in_string_format)


def handle_deposit_money_as_client():
    money_to_deposit = int(request.form.get("money"))
    login_id = int(request.form.get("login_id"))
    client = Bank.get_client_after_the_login_id(login_id)

    try:
        client.depositMoney(money_to_deposit)
        return render_success_template("Money deposited successfully")
    except BaseException as ex:
        return render_failure_template(str(ex))


def handle_withdraw_money_as_client():
    money_to_withdraw = int(request.form.get("money"))
    login_id = int(request.form.get("login_id"))
    client = Bank.get_client_after_the_login_id(login_id)

    try:
        client.withdrawMoney(money_to_withdraw)
        return render_success_template("Money withdrew successfully")
    except BaseException as ex:
        return render_failure_template(str(ex))


def handle_get_credit_request():
    money = int(request.form.get('money'))
    login_id = int(request.form.get('login_id'))
    nr_months = int(request.form.get('period'))

    client = Bank.get_client_after_the_login_id(login_id)
    ok = False
    try:
        ok = Bank.is_safe_to_give_the_credit(login_id, money, nr_months)
    except BaseException as exception:
        return render_failure_template(str(exception))

    if ok:
        rate_of_interest = Bank.get_rate_of_interest(nr_months)
        try:
            client.get_credit_from_bank(money, rate_of_interest, nr_months)
        except BaseException as exception:
            render_failure_template(str(exception))
        else:
            return render_success_template('You have got the credit')
    else:
        try:
            (nr_months, rate_of_interest) = Bank.get_offer(login_id, money)
            message = 'The bank cannot give you this credit on this period. ' + os.linesep
            message += 'Try to request that money on ' + str(
                nr_months) + ' months which will have the rate of interest ' + str(
                rate_of_interest) + "%. " + os.linesep
            message += 'Or you can simply request the money you want on a longer period' + os.linesep

            return render_failure_template(message)
        except BaseException as ex:
            render_failure_template(str(ex))


def handle_pay_debt_request():
    debt_id = int(request.form.get("debt_id"))
    login_id = int(request.form.get("login_id"))
    client = Bank.get_client_after_the_login_id(login_id)

    try:
        client.pay_debt(debt_id)
        return render_success_template("Debt paid successfully")
    except BaseException as ex:
        return render_failure_template(str(ex))


def handle_deposit_money_as_admin(bank):
    money = int(request.form.get("money"))
    login_id = int(request.form.get("login_id"))

    try:
        admin = bank.get_admin_after_the_login_id(login_id)
        admin.deposit_money_as_admin(money)
        return render_success_template("Money deposited successfully")
    except BaseException as exception:
        return render_failure_template(str(exception))


def handle_block_client_account_request(bank):
    client_s_login_id = int(request.form.get("client-login-id"))
    login_id_of_the_current_admin = int(request.form.get("login_id"))
    try:
        admin = bank.get_admin_after_the_login_id(login_id_of_the_current_admin)
        admin.block_client_account_after_the_login_id(client_s_login_id)
        return render_success_template("The client account was blocked")
    except BaseException as exception:
        return render_failure_template(str(exception))


def handle_unblock_client_account_request(bank):
    client_s_login_id = int(request.form.get("client-login-id"))
    login_id_of_the_current_admin = int(request.form.get("login_id"))
    try:
        admin = bank.get_admin_after_the_login_id(login_id_of_the_current_admin)
        admin.unblock_client_account_after_the_login_id(client_s_login_id)
        return render_success_template("The client account was unblocked")
    except BaseException as exception:
        return render_failure_template(str(exception))


def reload_client_page(bank):
    login_id = request.args.get('id')
    is_logged = bank.is_client_logged(login_id)
    if is_logged:
        client = bank.get_client_after_the_login_id(login_id)
        return get_client_template(client)
    raise ClientException("You are not logged in as a client. Please login first")


def reload_admin_page(bank):
    login_id = request.args.get('id')
    is_logged = bank.is_admin_logged(login_id)
    if is_logged:
        admin = bank.get_client_after_the_login_id(login_id)
        return get_admin_template(admin, bank)
    raise ClientException("You are not logged in as an admin. Please login first")


def get_client_template(client):
    message_for_general_information = str(client)
    return render_template('client.html', client=client,
                           message_for_general_information=message_for_general_information,
                           login_id=client.get_login_id())


def handle_money_transfer_request():
    try:
        sender_login_id = int(request.form.get("login_id"))
    except:
        print("naspa")
    receiver_login_id = int(request.form.get("destinator_id"))
    money_to_transfer = int(request.form.get("money"))

    try:
        sender_client = Bank.get_client_after_the_login_id(sender_login_id)
        receiver_client = Bank.get_client_after_the_login_id(receiver_login_id)
        sender_client.transfer_money(receiver_client, money_to_transfer)
    except BaseException as exception:
        return render_failure_template("There is no any client with the id: " + str(receiver_login_id))

    return render_success_template("Money transfered successfully")


@app.route('/client.html', methods=['POST', 'GET'])
def handle_client_request():
    bank = Bank("ING")
    if flask.request.method == 'POST':
        if request.form.get('post-type') == 'login':
            return handle_client_login_request(bank)
        elif request.form.get('post-type') == 'register':
            return handle_client_register_request(bank)
        elif request.form.get('post-type') == 'deposit':
            return handle_deposit_money_as_client()
        elif request.form.get('post-type') == 'withdraw':
            return handle_withdraw_money_as_client()
        elif request.form.get('post-type') == 'get_credit':
            return handle_get_credit_request()
        elif request.form.get('post-type') == 'pay_debt':
            return handle_pay_debt_request()
        elif request.form.get('post-type') == 'transfer':
            return handle_money_transfer_request()

        else:
            return render_failure_template('Something went wrong. Please try again later')
    else:
        try:
            return reload_client_page(bank)
        except ClientException as exception:
            return render_failure_template(str(exception))


@app.route('/admin.html', methods=['POST', 'GET'])
def handle_admin_request():
    bank = Bank("ING")
    if flask.request.method == 'POST':
        if request.form.get('post-type') == 'admin_login':
            return handle_admin_login_request(bank)
        elif request.form.get('post-type') == 'deposit-money':
            return handle_deposit_money_as_admin(bank)
        elif request.form.get('post-type') == 'block-client':
            return handle_block_client_account_request(bank)
        elif request.form.get('post-type') == 'unblock-client':
            return handle_unblock_client_account_request(bank)
        elif request.form.get('post-type') == 'create-admin':
            return handle_create_admin_request(bank)
        return render_failure_template('Something went wrong. Please try again later')
    else:
        try:
            return reload_admin_page(bank)
        except ClientException as exception:
            return render_failure_template(str(exception))


@app.route('/')
@app.route('/home.html')
def render_home_page_request():
    bank = Bank("ING")

    if request.args.get('mode') == '1':
        login_id = request.args.get('id')
        client = bank.get_client_after_the_login_id(login_id)
        client.set_log_field(False)
        return render_template('home.html')
    elif request.args.get('mode') == '2':
        login_id = request.args.get('id')
        try:
            admin = bank.get_admin_after_the_login_id(login_id)
            admin.set_log_field(False)
        except:
            return render_template('home.html')

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
