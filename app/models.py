# app/models.py

# Import von notwendigen Modulen für Datenmodell Klassen
import base64
import os
from datetime import datetime, timedelta        # datetime Module für Zeitfunktionen importieren
from app import db, login                       # Objekte aus __init__.py importieren
from flask_login import UserMixin               # UserMixin aus flask_login importieren
from werkzeug.security import generate_password_hash, check_password_hash # Module für Passwort-hash Funktionen aus Werkzeug importieren
from sqlalchemy.orm import relationship, backref #Module für SQLAlchemy importieren


# Klasse für User-Objekt / Tabelle definieren
class User(UserMixin, db.Model):

    # User-Attribute in User-Classe definieren - ID+Primärschnlüssel, Benutzername, Vorname, Nachname, Mailadresse, Password-Hash
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    firstname = db.Column(db.String(60), index=True)
    lastname = db.Column(db.String(60), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(190))

    # User-Token-Attribute für API Funktionen
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)


# Methoden für User Classe definieren
    def __repr__(self):
        return 'User {}'.format(self.username)
    
    # Methode zum Setzen eines Passworts - nutzt generate_password_hash aus werkzeug.security
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Methode zum Prüfen des eingegebenen Passworts - nutzt check_password_hash aus werkzeug.security
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)


    # API Methoden für API-Auhtentifizierung eines Users
    def get_token(self, expires_in=3600):    # Gültigkeit des Tokens in Sekunden 1 Stund
        now = datetime.utcnow()
    
        # Wenn Ablaufdatum des Tokens in der Zukunft liegt
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    
    # Token ungültig machen
    def revoke_token(self):
        # Ablaufdatum auf aktuelle Zeit - 1 sek. setzen
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        
    # Prüfung des Tokens
    @staticmethod
    def check_token(token):
        # SQL Abfrage ob eine Zeile für einen User mit dem mitgelieferten Token existiert
        user = User.query.filter_by(token=token).first()
        
        # Wenn das Token nicht existiert oder der Token abgelaufen ist, dann None zurückliefern, ansonsten das gefundene User-Objekt
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user



    # API Methoden für User-Class

    # Aus Unterrichtsmaterial
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email
        }
        return data
    
    # Aus Unterrichtsmaterial
    @staticmethod
    def to_collection():
        users = User.query.all()
        data = {
            'users': [result.to_dict() for result in users]
        }
        return (data)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Klasse für Purchase-Objekt / Tabelle definieren
class Purchase(db.Model):

    # Attribute in Purchase-Classe für Einkäufe definieren - Id und Primärschlüssel des Einkaufs, Firmenname bei der eingekauft worden ist,
    # Flag ob der Einkauf in Berechnungen mit einbezogen werden soll, Flag ob der Einkauf angezeigt werden soll, Id des Users, der den Einkauf erfasst hat
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    companyname = db.Column(db.String(120), index=True)
    calculate_costs = db.Column(db.Boolean, default=True)
    visible = db.Column(db.Boolean, default=True)
    id_user = db.Column(db.Integer, db.ForeignKey(User.id))

    # Items Attribut in Einkauf mit Relationship zu Items-Tabelle in Datenbank
    items = db.relationship(
        "Items", lazy="subquery", backref=backref("ItemPurchase", lazy="subquery")
    )

    # Für Print-Output debug eines Benutzerklassen-Objekts
    def __repr__(self):
        return 'Purchase {}'.format(self.date, self.items)

    # API Methoden für Einkäufe

    #  Methode für die Erstellung eines Dictionary für jeden Artikel eines Einkaufs
    def to_dict(self):
        
        item_list = {

            'items': []
        }

        for item in self.items:

            item_details = {

                'id': item.id,
                'name': item.name,
                'description': item.description,
                'amount': item.amount,
                'price_per': item.price_per,
                'item_type': item.item_type,
                'item_total': item.item_total
            }
            # Anhängen des aktuellen Item Dictionary
            item_list["items"].append(item_details)
        
        data = {
            'id': self.id,
            'date': self.date,
            'companyname': self.companyname,
        }
        # Anhängen der Item-Liste an das Rückgabe-Dictionary des Einkaufs
        data.update(item_list)
        return data

    # Methode für die Erstellung eines Dictionary für jeden Einkauf des Benutzers
    def to_dict_purchase(self):
        
        data = {
            'id': self.id,
            'date': self.date,
            'companyname': self.companyname,
        }
        return data

    # Methode für die Erstellung eines Dictionary für den Einkauf mit der angefragten purchase_id - nutzt Methode weiter oben .to_dict()
    @staticmethod
    def to_collection(user_id,purchase_id):
        #purchases = Purchase.query.filter_by(id_user=current_user.get_id()).order_by(Purchase.date.desc())
        purchases = Purchase.query.filter_by(id_user=user_id,id=purchase_id).order_by(Purchase.date.asc())
        data = {
            'Purchase': [result.to_dict() for result in purchases]
        }
        return (data)
    
    # Methode für die Erstellung eines Dictionary für Einkaufe des an der API authentifizierten Benutzers - nutzt Methode weiter oben .to_dict_purchase()
    @staticmethod
    def to_collection_purchases(user_id):
        #purchases = Purchase.query.filter_by(id_user=current_user.get_id()).order_by(Purchase.date.desc())
        purchases = Purchase.query.filter_by(id_user=user_id).order_by(Purchase.date.asc())
        data = {
            'Purchase': [result.to_dict_purchase() for result in purchases]
        }
        return (data)



    
# Klasse für Items-Objekt / Tabelle definieren
class Items(db.Model):

    # Id des Artikels und Primärschlüssel, Artikelname, Beschreibung, gekaufte Menge, Stückpreis, 
    # Id des Einkaufs als Fremdschlüssel, Preis für die Gesamte Menge des Artikels
    # Id des erfassenden Benutzers, Soll Artikel angezeigt werden, soll Artikel in Berechnung einbezogen werden
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    description = db.Column(db.String(1000), index=True)
    amount = db.Column(db.Integer)
    price_per = db.Column(db.Numeric(precision=10, scale=2, asdecimal=True))
    id_purchase = db.Column(db.Integer, db.ForeignKey(Purchase.id))
    item_type = db.Column(db.String(60), index=True)
    item_total = db.Column(db.Numeric(precision=10, scale=2, asdecimal=True))
    author_id = db.Column(db.Integer)
    visible = db.Column(db.Boolean, default=True)
    calculation_inclusion = db.Column(db.Boolean, default=True)


    def __repr__(self):
        return 'Items {}'.format(self.name)



# -- Aktuell noch nicht in Business-Logik implementiert
# Klasse für Maintenance-Objekt / Tabelle definieren
class Maintenance(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    name = db.Column(db.String(120), index=True)
    description = db.Column(db.String(1000), index=True)
    price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=True))
    id_item = db.Column(db.Integer, db.ForeignKey(Items.id))

    def __repr__(self):
        return 'Maintenance {}'.format(self.name)