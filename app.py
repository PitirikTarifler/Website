from flask import Flask,redirect,render_template, url_for,request,session,flash,jsonify,make_response
import sqlite3
import logging
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__,static_url_path='/static')

app.secret_key="SNEOD"
app.config['LOG_LEVEL'] = 'DEBUG'
app.logger.setLevel(logging.DEBUG)

@app.route("/")
def home():
    if 'user_id' in session and session["user_id"] is not None:
        connection = sqlite3.connect('pitirik.db')
        cursor=connection.cursor()
        cursor.execute("SELECT name FROM users WHERE id=?",(session["user_id"],))
        name=cursor.fetchone()
        connection.commit()
        connection.close()
        if name:
            return render_template("index.html",name=name[0])
        else:
            return render_template("index.html")
    return render_template("index.html")

@app.route("/suggestions",methods=["POST"])
def suggestions_form():
    name=request.form['name']
    surname=request.form['surname']
    email=request.form['email']
    message=request.form['message']
        
    connection = sqlite3.connect('pitirik.db')
    cursor=connection.cursor()
    cursor.execute("INSERT INTO suggestions (name,surname,email,message) VALUES(?,?,?,?)",(name,surname,email,message))

    connection.commit()
    connection.close()
    
    flash("Teşekkür ederiz!","info")
    return redirect(url_for('home'))

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        connection = sqlite3.connect('pitirik.db')
        cursor = connection.cursor()

        # Fetch all emails from the users table
        cursor.execute("SELECT email FROM users")
        emails = [row[0] for row in cursor.fetchall()]

        email = request.form['email']
        password_to_check = request.form['password']
        
        # Fetch the password for the provided email from the database
        cursor.execute("SELECT password FROM users WHERE email=?", (email,))
        fetched_password = cursor.fetchone()

        if email not in emails:
            flash("Kullanıcı bulunamadı.","error")
        elif check_password_hash(fetched_password[0],password_to_check) == False:
            flash("Parola doğru değil.","error")
        else: 
            cursor.execute("SELECT id FROM users WHERE password=? AND email=?",(fetched_password[0],email))
            user_id=cursor.fetchone()
            session["user_id"] = user_id[0]
            app.logger.info(f"User ID in session: {session.get('user_id')}")
            connection.close()
            return redirect(url_for('home'))
    return render_template("sign_in.html")

@app.route("/sign-up", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        connection = sqlite3.connect('pitirik.db')
        cursor=connection.cursor()
        name=request.form['name']
        surname=request.form['surname']
        email=request.form['email']
        password=request.form['password']
        repassword=request.form['repassword']

        cursor.execute("SELECT email FROM users")
        emails = [row[0] for row in cursor.fetchall()]

        hashed_password=generate_password_hash(password)
        if password != repassword:
            flash("Şifreler eşit değil!","error")
        elif  email in emails:
            flash("Bu eposta kullanılmış.","error")
        elif password == repassword and email != None:
            cursor.execute("INSERT INTO users (email,password,name,surname) VALUES(?,?,?,?)",(email,hashed_password,name,surname))
            cursor.execute("SELECT id FROM users WHERE password=? AND email=?",(hashed_password,email))
            user_id=cursor.fetchone()
            session["user_id"] = user_id[0]
            connection.commit()
            connection.close()
            return redirect(url_for('home'))
    return render_template("sign_up.html")

@app.route("/logout",methods=["GET"])
def logout():
    session.pop("user_id",None)
    return redirect(url_for('home'))

@app.route("/tarifler")
def tarifler():
    return render_template("tarifler.html")

@app.route("/tarifler/<category>")
def tarifler_category(category):
    connection=sqlite3.connect('pitirik.db')
    connection.row_factory = sqlite3.Row
    cursor=connection.cursor()

    cursor.execute("SELECT * FROM recipes where category=?",(category,))
    recipes=cursor.fetchall()

    cursor.execute("SELECT recipe_id,count, ingridient_name FROM recipe_ingridients JOIN ingridients ON ingridients.ingridient_id=recipe_ingridients.ingridient_id")
    recipe_ingridients=cursor.fetchall()

    connection.close()
    return render_template("tarifler_qued.html",recipes=recipes,category=category,recipe_ingridients=recipe_ingridients)

@app.route("/delete-account")
def deleteAcc():
    connection=sqlite3.connect('pitirik.db')
    cursor=connection.cursor()

    cursor.execute("DELETE FROM users WHERE id=?",(session["user_id"],))
    connection.commit()

    connection.close()
    session.pop("user_id",None)
    flash("Hesabınız başarıyla silinmiştir.","info")
    return redirect(url_for('home'))
@app.route("/yöresel/<region>")
def yoresel_category(region):
    connection=sqlite3.connect('pitirik.db')
    connection.row_factory = sqlite3.Row
    cursor=connection.cursor()

    cursor.execute("SELECT * FROM recipes where region=?",(region,))
    recipes=cursor.fetchall()

    cursor.execute("SELECT recipe_id,count, ingridient_name FROM recipe_ingridients JOIN ingridients ON ingridients.ingridient_id=recipe_ingridients.ingridient_id")
    recipe_ingridients=cursor.fetchall()

    connection.close()
    return render_template("yoresel_qued.html",recipes=recipes,region=region,recipe_ingridients=recipe_ingridients)

@app.route("/dolabım")
def dolabım():
    connection=sqlite3.connect('pitirik.db')
    connection.row_factory=sqlite3.Row
    cursor= connection.cursor()
    user_recipes= []

    cursor.execute("SELECT * FROM ingridients")
    ingridients=cursor.fetchall()

    cursor.execute("SELECT recipe_id,count, ingridient_name FROM recipe_ingridients JOIN ingridients ON ingridients.ingridient_id=recipe_ingridients.ingridient_id")
    recipe_ingridients=cursor.fetchall()

    cursor.execute("SELECT ingridient_name, user_ingridients.count  FROM ingridients JOIN user_ingridients ON ingridients.ingridient_id= user_ingridients.ingridient_id WHERE user_id=?",(session["user_id"],))
    owned_ingridients=cursor.fetchall()
    
    """ For the similar recipes """
    cursor.execute("SELECT * FROM recipes")
    recipes=cursor.fetchall()
    for recipe in recipes:
        if user_owns_recipe(session["user_id"],recipe['recipe_id']):
            user_recipes.append(recipe)
        
        
    connection.close()
    return render_template("dolabım.html",ingridients=ingridients,owned_ingridients=owned_ingridients,user_recipes=user_recipes,recipe_ingridients=recipe_ingridients)

@app.route("/user_recipes")
def user_owns_recipe(user_id,recipe_id):
    connection=sqlite3.connect('pitirik.db')
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    
    cursor.execute("SELECT ingridient_id FROM user_ingridients WHERE user_id=?;",(user_id,))
    user_ingridient_id=cursor.fetchall()

    cursor.execute("SELECT ingridient_id FROM recipe_ingridients WHERE recipe_id=?;",(recipe_id,))
    recipe_ingridient_id= cursor.fetchall()

    return all(ingredient in user_ingridient_id for ingredient in recipe_ingridient_id) 

@app.route("/yoresel")
def yoresel():
    return render_template("yoresel.html")

@app.route("/günün-menüsü")
def todaysmenu():
    return render_template("todaysmenu.html")

@app.route("/profil")
def profil():
    connection = sqlite3.connect('pitirik.db')
    cursor=connection.cursor()
    cursor.execute("SELECT name,surname,email FROM users WHERE id=?",(session["user_id"],))
    user_data=cursor.fetchone()
    connection.commit()
    connection.close()
    return render_template("profile.html",name=user_data[0],surname=user_data[1],email=user_data[2])

@app.route("/SSS")
def sss():
    return render_template("sss.html")

@app.route("/dolabım/add_ingridient", methods=["POST","GET"])
def add_ingridient():
    req=request.get_json()

    print(req)

    connection=sqlite3.connect('pitirik.db')
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    
    for rqst in req:
        cursor.execute("SELECT ingridient_id FROM ingridients WHERE ingridient_name=?", (rqst['ingridient_name'],))
        ingridient_id = cursor.fetchone()

        if ingridient_id:
            cursor.execute("SELECT ingridient_id FROM user_ingridients WHERE user_id=? AND ingridient_id=?", (session["user_id"], ingridient_id[0]))
            owned_ingridient_id = cursor.fetchone()

            if owned_ingridient_id:
                cursor.execute("UPDATE user_ingridients SET count=count + ? WHERE user_id=? AND ingridient_id=?", (rqst['count'], session["user_id"], ingridient_id[0]))
            else:
                cursor.execute("INSERT INTO user_ingridients (user_id, ingridient_id, count) VALUES (?, ?, ?)", (session["user_id"], ingridient_id[0], rqst['count']))
            connection.commit()
        else:
            print(f"Error: ingridient_id not found for {rqst['ingridient_name']}")

    connection.close()
    resp = make_response(jsonify(req), 200)
    connection.close()
    return resp

@app.route("/dolabım/remove_ingridient",methods=["POST"])
def remove_ingridient():
    req=request.get_json()
    print(req)

    connection=sqlite3.connect('pitirik.db')
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    for rqst in req:
        cursor.execute("SELECT count,user_ingridients.ingridient_id FROM user_ingridients JOIN ingridients ON ingridients.ingridient_id=user_ingridients.ingridient_id WHERE ingridient_name=?", (rqst['ingridient_name'],))
        owned_count_ingridient=cursor.fetchone()
        if rqst['count'] < owned_count_ingridient['count']:
            cursor.execute("UPDATE user_ingridients SET count=count-? WHERE user_id=? AND ingridient_id=?",(rqst['count'],session["user_id"],owned_count_ingridient['ingridient_id']))
        elif rqst['count'] == owned_count_ingridient['count']:
            cursor.execute("DELETE FROM user_ingridients WHERE ingridient_id=?",(owned_count_ingridient['ingridient_id'],))
        connection.commit()
    
    connection.close()
    resp=make_response(jsonify(req),200)
    return resp

if __name__ == "__main__":
    app.run(debug=False)

