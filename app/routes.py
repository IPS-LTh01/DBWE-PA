# app/routes.py

# Import von notwendigen Modulen für Routen
from flask import render_template, flash, redirect, url_for
from sqlalchemy import func, join
from app import app,db
from app.forms import LoginForm, RegisterForm, PurchaseForm, AddItemToPurchaseForm,EditItemInPurchaseForm,DeletePurchase,DeleteItem
from app.models import User, Purchase, Items, Maintenance
from flask_login import login_user, current_user, logout_user, login_required
# from flask import current_app


# Route für Hauptseite bei der das Template - index_derived.html gerendert wird
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('home.html', title='Home')


# Route für die Benutzerregistrierung bei der das Template - register.html im Fall des GET-Aufrufs gerender wird - bei der fehlerlosen Validierung wird der Benutzer angelegt
@app.route('/register', methods=['GET','POST'])
def register():
    
    # User auf /index zurückleiten, wenn bereits authentifiziert
    if current_user.is_authenticated:
        return redirect(url_for(index))
    
    # Laden der RegisterForm-Klasse in die form-variable
    form = RegisterForm()
    if form.validate_on_submit():
        # Wenn POST auf /register - Validierung und Umleitung auf die Login Route
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    # Wenn Get auf /register - Registrierungsformular anzeigen
    return render_template('register.html', title='Registrieren', form=form)


# Route für die Benutzeranmeldung bei der das Template - login.html im Fall des GET-Aufrufs gerender wird - bei der fehlerlosen Validierung wird der Benutzer angemeldet
@app.route('/login', methods=['GET','POST'])
def login():
    # User auf /index zurückleiten, wenn bereits authentifiziert
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Laden der Loginform-Klasse in die form-variable
    form = LoginForm()
    if form.validate_on_submit():
        # bei method=POST prüfen ob User existiert
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Ung&uuml;ltiger Benutzername oder Ung&uuml;ltiges Passwort')
            return redirect(url_for('login'))
        
        #Wenn prüfung OK -> Anmeldung udn Umleitung auf die Index-Route
        login_user(user, remember=form.remember_me.data)
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    # bei Get
    return render_template('login.html', title='Login', form=form)



# Route für die Logout-Funktion und Umleitung auf die Index-Route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Route für die Ansicht zur Auflistung aller erfassten Einkäufe des Benutzers
@app.route('/view-purchases', methods=['GET','POST'])
def view_purchases():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Query per SQLAlchemy für erfasste Einkäufe, die calculate_costs=1 und visible=1 haben
    results_purchases = Purchase.query.filter_by(id_user=current_user.get_id(),calculate_costs=1,visible=1).order_by(Purchase.date.desc())
    return render_template('view_purchases.html', title='Einkäufe - Übersicht', purchases=results_purchases)


# Route zum Erfassen von neuen Einkäufen durch den Benutzer
@app.route('/submit-purchase', methods=['GET','POST'])
def submit_purchase():
    
    # Benutzer auf /index zurückleiten, gültige Anmeldung existiert
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Laden der PurchaseForm-Klasse in die form-variable
    form = PurchaseForm()

    # Bei erfolgreicher Validierung des Formulars während der Post Methode, wird der Einkauf in der Datenbank durch SQL-Alchemy angelegt - Bei der POST-Methode wird das Template: submit_purchase.html gerendert
    if form.validate_on_submit():
        purchase = Purchase(companyname=form.companyname.data,id_user=current_user.get_id())
        db.session.add(purchase)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('submit_purchase.html', title='Einkauf erfassen', form=form)

# Route zum Löschen eines Einkaufs 
@app.route('/delete-purchase/<int:purchase_id>', methods=['GET','POST'])
def delete_purchase(purchase_id):

    # Benutzer auf /index zurückleiten, gültige Anmeldung existiert
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Laden der DeletePurchase-Klasse in die form-variable
    purchase = Purchase.query.filter_by(id_user=current_user.get_id(),id=purchase_id).first()
    
    form = DeletePurchase()

    
    # Wenn das Form validiert wird, also wenn der Benutzer zustimmt, dass der Einkauf gelöscht werden soll
    if form.validate_on_submit():
        
        # Wenn ein Einkauf gefunden worden ist, welche die angegebene ID hat und dessen id_user gleich der User-Id des aktuellen Benutzers ist
        if purchase is not None:
            # Auf dem Einkauf wird gesetzt, dass er nicht mehr in Berechnungen einbezogen werden soll und in der App nicht mehr angezeigt werden soll
            purchase.calculate_costs = 0
            purchase.visible = 0
            db.session.commit()
            return redirect(url_for('view_purchases'))
        else:
            # Wenn kein Einkauf vorhanden ist dessen id_user gleich der aktuellen User-Id ist
            return redirect(url_for('view_purchases'))
    return render_template('delete_purchase.html', title='Einkauf löschen', form=form)

# Route zum Anzeigen aller Artikel die unter einem Einkauf mit der "purchase_id" in der Route erfasst worden sind
@app.route('/purchases/<int:purchase_id>', methods=['GET','POST'])
def display_purchase(purchase_id):
    
    # Benutzer auf /index zurückleiten, gültige Anmeldung existiert
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if not Purchase.query.filter_by(id_user=current_user.get_id(),id=purchase_id):
        return redirect(url_for('index'))


    #items = Items.query.filter_by(id_purchase=purchase_id).add_columns()
    items = Items.query.filter_by(id_purchase=purchase_id,visible=1,calculation_inclusion=1)

    return render_template('edit_purchase.html', title='Einkauf bearbeiten', items=items, id_purchase=purchase_id)


# Route für das Formular zu Hinzufügen eines Artikels zu einem Einkauf
@app.route('/additem/<int:purchase_id>', methods=['GET','POST'])
def add_item_to_purchase(purchase_id):

    # Benutzer auf /index zurückleiten, gültige Anmeldung existiert
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if not Purchase.query.filter_by(id_user=current_user.get_id(),id=purchase_id):
        return redirect(url_for('index'))
    
    # Laden der AddItemToPurchaseForm-Klasse in die form-variable
    form = AddItemToPurchaseForm()
    purch_id = purchase_id

    # Wenn Validierung des Form keine Fehler hat
    if form.validate_on_submit():
        
        item = Items(
            name=form.itemname.data,
            item_type=form.itemtype.data,
            amount=form.itemamount.data,
            price_per=form.itempriceper.data,
            description=form.itemdescription.data,
            id_purchase=purchase_id,
            author_id=current_user.get_id(),
            item_total=round((form.itemamount.data*form.itempriceper.data),2))
        db.session.add(item)
        db.session.commit()
        
        return redirect(url_for('view_purchases'))
    
    return render_template('add_item_toPurchase.html', title='Artikel hinzufügen', id_purchase=purchase_id, form=form)


# Route für das Formular zu Bearbeiten eines Artikels mit der item_id in einem bestehenden Einkauf
@app.route('/edititem/<int:item_id>', methods=['GET','POST'])
def edit_item_in_purchase(item_id):

    item = Items.query.filter_by(id=item_id,author_id=current_user.get_id()).first()

    # Benutzer auf /index zurückleiten, gültige Anmeldung existiert
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Laden der EditItemInPurchaseForm-Klasse in die form-variable
    form = EditItemInPurchaseForm()
    if form.validate_on_submit():
        
        # Wenn der Artikel mit der angegebenen ID gefunden worden ist und dessen id_user gleich der User-Id des aktuellen Benutzers ist
        if item is not None:
            item.id=item_id
            item.name=form.itemname.data,
            item.item_type=form.itemtype.data,
            item.amount=form.itemamount.data,
            item.price_per=form.itempriceper.data,
            item.description=form.itemdescription.data,
            item.item_total=round((form.itemamount.data*form.itempriceper.data),2)
            db.session.commit()
            return redirect('/purchases/'+ str(item.id_purchase))
        else:
            # Wenn item keinen Eintrag zurückgeliefert hat Umleitung auf die Detailseite des Einkaufs
            return redirect('/purchases/'+ str(item.id_purchase))
    
    return render_template('edit_item_inPurchase.html', title='Artikel bearbeiten', items=item, form=form)


#@app.route('/edititem/<int:item_id>', methods=['GET'])
#def display_purchases_with_totals():

#    result = db.select()

# Route zum Löschen eines Artikels eines Einkaufs 
@app.route('/delete-item/<int:item_id>', methods=['GET','POST'])
def delete_item(item_id):

    # Benutzer auf /index zurückleiten, gültige Anmeldung existiert
    if not current_user.is_authenticated:
        return redirect('index')
    
    # Laden der DeletePurchase-Klasse in die form-variable
    item = Items.query.filter_by(id=item_id,author_id=current_user.get_id()).first()
    
    form = DeleteItem()

    # Wenn das Form validiert wird, also wenn der Benutzer zustimmt, dass der Einkauf gelöscht werden soll
    if form.validate_on_submit():
        # Wenn der Artikel mit der angegebenen ID gefunden worden ist und dessen id_user gleich der User-Id des aktuellen Benutzers ist
        if item is not None:
            # Auf dem Artikel wird gesetzt, dass es nicht mehr in Berechnungen einbezogen werden soll und in der App nicht mehr angezeigt werden soll
            item.calculation_inclusion = 0
            item.visible = 0
            db.session.commit()
            return redirect(url_for('view_purchases'))
        else:
            # Wenn item keinen Eintrag zurückgeliefert hat Umleitung auf die Detailseite der Einkäufe
            return redirect('/purchases/')
    return render_template('delete_item.html', title='Artikel löschen', form=form)