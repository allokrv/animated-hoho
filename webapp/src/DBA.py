from app import ws
from pg import DB
import time

db = None


def init_db():
    global db
    for i in range(10):
        try:
            db = DB(dbname='db',
                    host='db', port=5432,
                    user='admin', passwd='nimda')
            print("Connection established")
            return
        except Exception:
            print("No Connection to db, retrying ..")
            time.sleep(1)
            continue


init_db()


class UserData:
    global db
    id       = None
    mail     = None
    username = None
    passhash = None
    is_active = True
    is_authenticated = False
    is_anonymous = False

    def __init__(self, name, email, pwhash):
        self.username = name
        self.passhash = pwhash
        self.mail     = email

    def check_passhash(self, passw):
        qry = "SELECT passhash,mail FROM users "
        qry += "WHERE username='"+self.username+"'"
        r = db.query(qry)
        r = r.dictresult()
        if len(r) < 1:
            return False
        if ws.check_password_hash(r[0]["passhash"], passw):
            self.passhash = r[0]["passhash"]
            self.mail = r[0]["mail"]
            self.is_authenticated = True
            return True
        else:
            return False

    def get_id(self):
        return self.username

    def printall(self):
        print("Name: %s" % self.username)
        print("Mail: %s" % self.mail)
        print("Pass: %s" % self.passhash)
        print("Auth: %r" % self.is_authenticated)

    def submit_to_db(self):
        if None in [self.username, self.passhash, self.mail]:
            raise Exception("None in UserData class, can't submit to db!")
        else:
            return self.submit()

    def submit(self):
        qry = "SELECT * FROM users "
        qry += "WHERE username='"+self.username+"';"
        r = db.query(qry)
        if r.one() is None:
            print("Sending User-Creation request for %s" % self.username)
            qry = "INSERT INTO users(username, mail, passhash) VALUES ('"
            qry += self.username + "', '" + self.mail + "', '" + self.passhash + "');"
            r = db.query(qry)
            return True
        else:
            return False


def getAll():
    if db is None:
        init_db()
    return db.query("SELECT * FROM users")
    # return db.query("SELECT table_name FROM information_schema.tables WHERE table_schema='public'  AND table_type='BASE TABLE';")


def getUserByName(uname):
    qry = "SELECT username, passhash, mail FROM users WHERE username='%s'" % uname
    r = db.query(qry).dictresult()
    if len(r) < 1:
        return None
    else:
        _data = UserData(r[0]["username"], r[0]["mail"], r[0]["passhash"])
        _data.is_authenticated = True
        return _data