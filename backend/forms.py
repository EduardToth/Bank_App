from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField , SubmitField , BooleanField , TextAreaField
from wtforms.validators import DataRequired , Length , Email , EqualTo , ValidationError


class RequestResetForm ( FlaskForm ) :
    email = StringField ( 'Please enter the email associated with your account:' ,
                          validators = [DataRequired ( ) , Email ( )] )
    submit = SubmitField ( 'Request Password Reset' )


class ResetPasswordForm ( FlaskForm ) :
    password = PasswordField ( 'Password' , validators = [DataRequired ( )] )
    confirm_password = PasswordField ( 'Confirm Password' ,
                                       validators = [DataRequired ( ) , EqualTo ( 'password' )] )
    submit = SubmitField ( 'Reset Password' )
