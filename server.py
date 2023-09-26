from flask import Flask, render_template, redirect, flash, request, session
from forms import LoginForm
import jinja2
import melons, customers

app = Flask(__name__)
app.secret_key = 'dev'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def homepage():
    return render_template("base.html")

@app.route("/melons")
def all_melons():

    melon_list = melons.get_all()
    return render_template("all_melons.html", melon_list=melon_list)

@app.route("/melon/<melon_id>")
def melon_details(melon_id):

    melon = melons.get_by_id(melon_id)
    return render_template("melon_details.html", melon=melon)

@app.route("/add_to_cart/<melon_id>", methods=["POST"])
def add_to_cart(melon_id):

    if 'username' not in session:
        flash("Please sign in to continue shopping")
        return redirect("/login")

    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']

    quantity = int(request.form.get('quantity', 1))

    if quantity < 1:
        flash('Invalid quantity')
        return redirect(request.referrer)
    
    cart[melon_id] = cart.get(melon_id, 0) + quantity
    session.modified = True
    flash(f"{quantity} melons of {melon_id} added to cart.")

    return redirect("/cart")


@app.route("/cart")
def show_cart():
    order_total = 0
    cart_melons = []

    cart = session.get("cart", {})

    for melon_id, quantity in cart.items():
        melon = melons.get_by_id(melon_id)

        total_cost = quantity * melon.price
        order_total += total_cost

        melon.quantity = quantity
        melon.total_cost = total_cost

        cart_melons.append(melon)

    return render_template("cart.html", cart_melons=cart_melons, order_total=order_total)

@app.route("/empty-cart")
def empty_cart():
    session["cart"] = {}

    return redirect("/cart")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
    
        user = customers.get_by_username(username)

        if not user or user['password'] != password:
            flash("invalid username or password")
            return redirect('/login')

        session["username"] = user['username']
        flash("Logged in.")
        return redirect("/melons")
    
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    del session["username"]
    flash("Logged Out")
    return redirect("/login")


@app.errorhandler(404)
def error_404(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.env = "developement"
    app.run(debug = True, port = 8000, host = "localhost")