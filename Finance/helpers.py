import os
import requests
import urllib.parse

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps


db = SQL("sqlite:///finance.db")


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", top=code, bottom=message), code


def init(session):
    uid = session
    init = db.execute("SELECT money.init FROM money JOIN users ON users.id = money.id WHERE users.id = ?", uid)
    if len(init) > 0:
        return init[0]["init"]
    else:
        return 0


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def conf(amount, name, price, symbol):
    return f"<h2 style=\"display: inline;\"> Buy </h2><h2 style=\"display: inline; color:#bb1111;\">{amount} </h2><h2 style=\"display: inline;\"> share(s) of </h2><h2 style=\"display: inline; color:#bb1111;\">{name} </h2><h2 style=\"display: inline;\">for $</h2><h2 style=\"display: inline; color:#226633;\">{price:.2f}</h2><h2 style=\"display: inline;\">?</h2><form action=\"/buy\" method=\"post\"><input type=\"hidden\" id=\"symbol\" name=\"symbol\" value='{symbol}'><input type=\"hidden\" id=\"amount\" name=\"amount\" value='c{amount}'><button type= \"submit\" style=\"display: inline; margin: 5px\" class=\"btn btn-success\">Yes</button></form><form action=\"/buy\"><button style=\"display: inline; margin: 5px\" class=\"btn btn-danger\">No</button></form>"