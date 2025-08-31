# app/api.py

# Import von notwendigen Modulen für die API-Endpunkte
from app import app, db
from app.models import User, Purchase
from flask import jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.errors import error_response


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

# API Endpunkte für Einkäufe
@app.route('/api/purchase/<int:id>', methods=['GET'])
@token_auth.login_required
def get_purchase(id):
    data = Purchase.to_collection(token_auth.current_user().get_id(),id)
    return jsonify(data)


@app.route('/api/purchases', methods=['GET'])
@token_auth.login_required
def get_purchases():
    data = Purchase.to_collection_purchases(token_auth.current_user().get_id())
    return jsonify(data)



##################
# Endpunkte für API-Authentifizierung

@app.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})


#Route um Token des über die API mittels Delete Methode ungültig zu machen
@app.route('/api/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204



# API - angegebenes Passwort des basic_auth-Objekts prüfen
@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

# API - Error Handler des basic_auth objekts
def basic_auth_error(status):
    return error_response(status)


# Zum Verifizieren des Tokens für ein token_auth Objekts
@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

# Error handler für token_auth Object
@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)
