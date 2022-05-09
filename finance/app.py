import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, make_response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd, init, conf
from datetime import date

username = 0
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return redirect("/home", 200)


@app.route("/home/", methods=["GET", "POST"])
@login_required
def home():
    if init(session["user_id"]) == 0:
        return redirect("/cash")
    """Show portfolio of stocks"""
    uid = session["user_id"]
    stocks = db.execute("SELECT shares FROM shares WHERE id = ?", uid)
    try:
        stocks = stocks[0]["shares"].split()
    except:
        stocks = []
    sh = stocks[1::2]
    for element in sh:
        sh[sh.index(element)] = int(element)
    stocks = stocks[0::2]
    names = []
    prices = []
    for element in stocks:
        names.append(lookup(element)["name"])
        prices.append(lookup(element)["price"])
    total = 0
    cash = round(db.execute("SELECT cash FROM money WHERE id = ?", uid)[0]["cash"], 2)
    for element in sh:
        total += element * prices[sh.index(element)]
    total += cash
    total = round(total, 2)
    return render_template("/home.html", stocks=stocks, sh=sh, names=names, cash=cash, prices=prices, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if init(session["user_id"]) == 0:
        return redirect("/cash")
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        amount = request.form.get("amount")
        if symbol == None:
            symbol = request.form.get("symbolm")
        if amount == None:
            amount = request.form.get("amountm")
        # if confirmed buy
        if amount[0] == 'c':
            amount = amount[1:]
            amount = int(amount)
            price = round(float(lookup(symbol)["price"]), 2)
            uid = session["user_id"]
            # get cash, deduct, and update database
            cash = db.execute("SELECT cash FROM money WHERE id = ?", uid)[0]["cash"]
            cash -= price * amount
            db.execute("UPDATE money SET cash = ? WHERE id = ?", cash, uid)
            # get shares from database (shares in the database are saved as a string - e.g. 'GOOG 2 APPL 5')
            shares = db.execute("SELECT shares FROM shares WHERE id = ?", uid)
            try:
                shares = shares[0]["shares"].split()
            except:
                shares = []
            # if user has bought shares - update them, else - add shares and amount
            if symbol in shares:
                ind = shares.index(symbol)
                shares[ind + 1] = str(int(shares[ind + 1]) + amount)
            else:
                shares.append(symbol)
                shares.append(str(amount))
            # convert shares back to string and update database
            shares = ' '.join(shares)
            db.execute("UPDATE shares SET shares = ? WHERE id = ?", shares, uid)
            name = lookup(symbol)["name"]
            # update history table
            dt = date.today().strftime("%B %d, %Y")
            db.execute("INSERT INTO history (userid, date, symbol, name, shares, op, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       uid, dt, symbol, name, amount, 'buy', price)
            flash(f'Successfully bought {amount} share(s) of {name}')
            return redirect("/home")
        amount = int(amount)
        price = 0
        name = ' '
        if lookup(symbol) != None:
            price = float(lookup(symbol)["price"])
            name = lookup(symbol)["name"]
        price *= amount
        cash = db.execute("SELECT cash FROM money WHERE id = ?", session["user_id"])[0]["cash"]
        print(cash)
        if price > cash:
            flash('You cannot afford that!')
            return render_template("buy.html")
        else:
            print(price, name, amount)
            confirm = conf(amount, name, price, symbol)
            return render_template("buy.html", confirm=confirm)

    return render_template("/buy.html")


@app.route("/history")
@login_required
def history():
    uid = session["user_id"]
    if init(uid) == 0:
        return redirect("/cash")
    """Show history of transactions"""
    history = reversed(db.execute("SELECT * FROM history WHERE userid = ?", uid))
    return render_template("/history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("username not filled", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("password not filled", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        if init(session["user_id"]) == 0:
            return redirect("/cash", 200)

        # Redirect user to home page
        return redirect("/home", 200)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/home")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if init(session["user_id"]) == 0:
        return redirect("/cash")
    if request.method == 'POST':
        symbol = request.form.get("symbol")
        if symbol == None:
            symbol = request.form.get("symbolm")
        price = 0
        name = ' '
        if lookup(symbol) != None:
            price = lookup(symbol)["price"]
            name = lookup(symbol)["name"]
        if int(price) > 0:
            print(price)
            return render_template("quote.html", price=price, name=name)
        else:
            flash('Invalid symbol!')
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'POST':
        user = request.form.get("username")
        pass1 = request.form.get("password")
        pass2 = request.form.get("confirmation")
        users = db.execute("SELECT * FROM users WHERE username = ?", user)
        if len(users) > 0:
            flash('Username not available')
            return redirect("/register", 400)
        elif pass1 != pass2:
            flash('Passwords do not match')
            return redirect("/register", 400)
        elif not user:
            flash('Username field not filled')
            return redirect("/register", 400)
        elif not pass1:
            flash('Password field not filled')
            return redirect("/register", 400)
        elif len(pass1) < 6 or len(pass1) > 20:
            flash('Password does not fulfil specifications')
            return redirect("/register", 400)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", user, generate_password_hash(pass1))
            userid = db.execute("SELECT id FROM users WHERE username = ?", user)
            userid = userid[0]["id"]
            init = 0
            db.execute("INSERT INTO money (init, id) VALUES(?, ?)", init, userid)
            db.execute("INSERT INTO shares (id) VALUES(?)", userid)
            flash('Register successful')
            session["user_id"] = userid
            return redirect("/cash", 200)
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    uid = session["user_id"]
    if init(uid) == 0:
        return redirect("/cash")
    if request.method == "POST":
        symbol = request.form.get("symbol")
        amount = request.form.get("amount")
        amount = int(amount)
        shares = db.execute("SELECT shares FROM shares WHERE id = ?", uid)
        shares = shares[0]["shares"].split()
        if int(shares[shares.index(symbol) + 1]) - amount > 0:
            shares[shares.index(symbol) + 1] = str(int(shares[shares.index(symbol) + 1]) - amount)
        else:
            shares.pop(shares.index(symbol) + 1)
            shares.pop(shares.index(symbol))
        shares = ' '.join(shares)
        gain = amount * int(lookup(symbol)["price"])
        cash = round(db.execute("SELECT cash FROM money WHERE id = ?", uid)[0]["cash"], 2)
        cash += gain
        dt = date.today().strftime("%B %d, %Y")
        db.execute("UPDATE money SET cash = ? WHERE id = ?", cash, uid)
        db.execute("INSERT INTO history (userid, date, symbol, name, shares, op, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   uid, dt, symbol, lookup(symbol)["name"], amount, 'sell', lookup(symbol)["price"])
        db.execute("UPDATE shares SET shares = ? WHERE id = ?", shares, uid)
        flash(f'Successfully sold {amount} share(s) of {lookup(symbol)["name"]}')
    stocks = db.execute("SELECT shares FROM shares WHERE id = ?", uid)
    try:
        stocks = stocks[0]["shares"].split()
    except:
        stocks = []
    sh = stocks[1::2]
    for element in sh:
        sh[sh.index(element)] = int(element)
    stocks = stocks[0::2]
    names = []
    prices = []
    for element in stocks:
        names.append(lookup(element)["name"])
        prices.append(lookup(element)["price"])
    total = 0
    cash = round(db.execute("SELECT cash FROM money WHERE id = ?", uid)[0]["cash"], 2)
    for element in sh:
        total += element * prices[sh.index(element)]
    total += cash
    return render_template("/sell.html", stocks=stocks, sh=sh, names=names, cash=cash, prices=prices, total=total)


@app.route("/cash/", methods=["GET", "POST"])
@login_required
def check():
    cashm = request.form.get("manual")
    cash1k = request.form.get("1k")
    cash10k = request.form.get("10k")
    cash1m = request.form.get("1m")
    casha = [cashm, cash1k, cash10k, cash1m]
    cash = 0
    inits = 0
    for i in casha:
        if i != None:
            cash = i
            inits = 1
    uid = session["user_id"]
    dt = date.today().strftime("%B %d, %Y")
    db.execute("UPDATE money SET init = ?, cash = ? WHERE id = ?", inits, cash, uid)
    if init(uid) == 0:
        return render_template("cash.html")
    else:
        db.execute("INSERT INTO history (userid, date, name, op, price) VALUES(?, ?, ?, ?, ?)",
                   uid, dt, 'Account created', 'Starting money', cash)
        return redirect("/home")


@app.route("/test")
def what():
    return render_template("test.html")

