import os

import flask

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, flash, redirect, request
from backend.forms import ResetPasswordForm, RequestResetForm
from backend.Bank import Bank
from backend.ClientException import ClientException
import hashlib

from flask_mail import Mail

from flask_mail import Message

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Edy:Edy_password@localhost/Bank2'
db = SQLAlchemy(app)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bankappCDE'
app.config['MAIL_PASSWORD'] = 'bankapp1234'
mail = Mail(app)


class Admins(db.Model):
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), unique=True)
    id = db.Column(db.Integer, unique=True, primary_key=True)
    email = db.Column(db.String(50))
    is_logged = db.Column(db.Integer)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Admins.query.get(user_id)


class Clients(db.Model):
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), unique=True)
    moneyOwned = db.Column(db.Integer)
    debt = db.Column(db.Integer)
    login_id = db.Column(db.Integer, unique=True, primary_key=True)
    blocked = db.Column(db.Integer)
    is_logged = db.Column(db.Integer)
    postal_code = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    email = db.Column(db.String(50))
    monthly_income = db.Column(db.Integer)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.login_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Clients.query.get(user_id)


def render_success_template(success_message):
    return render_template('successTemplate.html', success_message=success_message)


def render_failure_template(error_message):
    return render_template('failureTemplate.html', error_message=error_message)


def handle_client_register_request(bank):
    name = request.form.get('name')
    password = request.form.get('password')
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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('.reset_token', token=token, user=user, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request_client():
    form = RequestResetForm()
    if form.validate_on_submit():
        client = Clients.query.filter_by(email=form.email.data).first()
        if client is None:
            flash('That email does not exist in our database!', 'warning')
        else:
            send_reset_email(client)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('render_home_page_request'))
    return render_template('reset_request.html', form=form)


@app.route("/reset_password/admin", methods=['GET', 'POST'])
def reset_request_admin():
    form = RequestResetForm()
    if form.validate_on_submit():
        admin = Admins.query.filter_by(email=form.email.data).first()
        if admin is None:
            flash('That email does not exist in our database!', 'warning')
        else:
            send_reset_email(admin)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('render_home_page_request'))
    return render_template('reset_request.html', form=form)


@app.route("/reset_password/<token>/<user>", methods=['GET', 'POST'])
def reset_token(token, user):
    c = user[1]
    if c == 'C':
        user = Clients.verify_reset_token(token)
    else:
        user = Admins.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        if c == 'C':
            return redirect(url_for('reset_request_client'))
        else:
            return redirect(url_for('reset_request_admin'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        passwordHashed = hashlib.md5((form.password.data).encode("utf-8"))
        passwordHexa = passwordHashed.hexdigest()
        user.password = passwordHexa
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('render_home_page_request'))
    return render_template('reset_token.html', title='Reset Password', form=form)


if __name__ == '__main__':
    app.run(debug=True)
