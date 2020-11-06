from flask import Flask, render_template, request, redirect
from flask_login import AnonymousUserMixin
import werkzeug.security as ws
from time import strftime
import flask_login
import DBA


# flask_login.UserMixin
print("Starting Webshop..")
app = Flask(__name__, template_folder='../html', static_folder="../html/static")
app.config['SECRET_KEY'] = 'ThisIsSuperSecretSoL34v3MeTheFuckAlone'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = "guest"


login_manager.anonymous_user = Anonymous

# Home / index.html
@app.route('/')
@app.route('/home')
@app.route('/index')
def home():
    # provisional product query
    # add a db query here to the products table
    products = [{   "product-name": "Santa-Head",
                    "price":        "4.20",
                    "desc":         "A fancy and long description, describing the product",
                    "img":          "o1.png"    },
                {   "product-name": "A Fly Thingy",
                    "price":        "8.40",
                    "desc":         "Another fancy and long description, describing the product",
                    "img":          "o2.png"    },
                {   "product-name": "Reindeer",
                    "price":        "12.60",
                    "desc":         "This is getting really annoying",
                    "img":          "o3.png"    },
                {   "product-name": "A f*cking Sock?!",
                    "price":        "199.99",
                    "desc":         "In case you're wondering: it's only 1",
                    "img":          "o4.png"    },
                {   "product-name": "A Surprise",
                    "price":        "25.00",
                    "desc":         "It might actually be shit packed in a box",
                    "img":          "o5.png"    }]
    return render_template("index.html", strftime=strftime('%B %dth %Y'), items=products, current_user=flask_login.current_user)


# User loader: LEAVE AS IS flask background stuffs..
@login_manager.user_loader
def loadu(username):
    return DBA.getUserByName(username)


# LOCK FOR RELEASE BUILDS!
@app.route('/admin-debug')
def admin_debug():
    _debuginfo = DBA.getAll()
    return render_template("debug.html", debuginfo=_debuginfo)


@app.route('/login')
def login():
    return render_template("login.html")


@app.route("/logout")
@flask_login.login_required
def logout():
    print("User '%s' just logged out, bb!" % flask_login.current_user.username)
    flask_login.logout_user()
    return redirect("index")


@app.route('/register')
def register():
    return render_template("register.html")


# checks if register-data is valid
@app.route('/registercheck', methods=['GET', 'POST'])
def registercheck():
    _name = request.form['name']
    if not _name.isalpha():
        _name = ""
    _email = request.form['email']
    # hashing the password asap (PBKDF2:SHA256 Salt 8)
    _password = ws.generate_password_hash(request.form['password'])
    if _password == "" or _email == "" or _name == "":
        return render_template("RegisterFailed.html")
    else:
        # submitting data to DB
        _data = DBA.UserData(name=_name, email=_email, pwhash=_password)
        done = _data.submit_to_db()  # returns 0 if it fails
        if not done:
            return render_template("RegisterFailed.html")

        return render_template("RegisterSuccess.html", name=_name, email=_email)


# checks if login-data is valid
@app.route('/logincheck', methods=['GET', 'POST'])
def logincheck():
    # global user
    _name = request.form['name']
    if not _name.isalpha():
        _name = ""
    _password = request.form['password']
    _data = DBA.UserData(_name, None, None)
    # using dedicated werkzeug passhash check
    correct = _data.check_passhash(_password)
    _debug = []
    if correct:
        print("User '%s' just logged in from %s" % (_name, request.remote_addr))
        flask_login.login_user(_data)
        return redirect("index")
    else:
        print("Failed login attempt on Account: '%s' from %s" % (_name, request.remote_addr))
        _debug.append("Login Failed!")
    return render_template("debug.html", debuginfo=_debug)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
