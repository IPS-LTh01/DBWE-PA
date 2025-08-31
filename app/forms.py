# app/forms.py

# Import von notwendigen Modulen für die Formularklassen
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange
from app.models import User

# Klasse für Anmeldeformular und dessen Felder
class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

# Klasse für Benutzer-Registrationsformular und dessen Felder
class RegisterForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    activation = StringField('Aktivierungscode (Siehe Anhänge)', validators=[DataRequired()])
    submit = SubmitField('Registrieren')

    # Methode zur Prüfung, ob der Beutzer bereits existiert
    def validate_username(self,username):

        #Abfrage über SQLAlchemy ob ein Benutzer mit dem eingegebenen Name ein Resultat zurückliefert
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bitte anderen Benutzername verwenden.')

    # Methode zur Prüfung, ob die Mailadresse bereits existiert    
    def validate_email(self,email):

        #Abfrage über SQLAlchemy ob ein Benutzer mit dem eingegebenen Mailadresse ein Resultat zurückliefert
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte eine andere Mailadresse verwende.')

    # Prüfung ob ein gültiger Aktivierungscode während der Registrierung angegeben worden ist, aktuell Hardcoded     
    def validate_activation(self,activation):

        if not activation.data == 'Welcome@2025':
            raise ValidationError('Bitte einen gültigen Aktivierunscode eingeben.')

# Klasse für Formular um den Einkauf bei einer Firma zu erfassen
class PurchaseForm(FlaskForm):
    companyname = StringField('Einkauf bei Firma: ', validators=[DataRequired()])
    submit = SubmitField('Erfassen')

# Klasse für Formular um erfassten Einkauf zu löschen
class DeletePurchase(FlaskForm):
    submit = SubmitField('Löschen')

# Klasse für das Formular um einem Einkauf einen Artikel hinzuzufügen - Mit Name, Art, Menge, Stückpreis und Beschreibung 
class AddItemToPurchaseForm(FlaskForm):
    itemname = StringField('Artikel-Name', validators=[DataRequired()])
    itemtype = StringField('Artikel-Art', validators=[DataRequired()])
    itemamount = IntegerField('Menge', validators=[DataRequired(), NumberRange(min=1, max=9999999)])
    itempriceper = FloatField('Stückpreis', validators=[DataRequired(), NumberRange(min=0.01, max=9999999)])
    itemdescription = StringField('Artikel-Beschreibung', validators=[DataRequired()])
    submit = SubmitField('Erfassen')


# Klasse für das Formular um einen bereits erfassen Artikel zu bearbeiten - Enthält die gleichen Formularfelder
class EditItemInPurchaseForm(FlaskForm):
    itemname = StringField('Artikel-Name', validators=[DataRequired()])
    itemtype = StringField('Artikel-Art', validators=[DataRequired()])
    itemamount = IntegerField('Menge', validators=[DataRequired(), NumberRange(min=1, max=9999999)])
    itempriceper = FloatField('Stückpreis', validators=[DataRequired(), NumberRange(min=0.01, max=9999999)])
    itemdescription = StringField('Artikel-Beschreibung', validators=[DataRequired()])
    submit = SubmitField('Anpassen')


# Klasse für Formular um erfassten Artikel eines Einkaufs zu löschen
class DeleteItem(FlaskForm):
    submit = SubmitField('Löschen')