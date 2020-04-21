from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bank'
db = SQLAlchemy(app)


class Admins(db.Model):
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), unique=True)
    id = db.Column(db.Integer, unique=True, primary_key=True)
    is_logged = db.Column(db.Integer)

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