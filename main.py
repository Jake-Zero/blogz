from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://build-a-blog:jacoblog@localhost:3306/build-a-blog'
app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = "dsovmodvsodmvmosoifomvfvfemfvmavfmvf"

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/blog")
def blog_listings():
    blogs = Blog.query.all()
    id = request.args.get("id")
    user_id = request.args.get("user")
    if id:
        blog = Blog.query.filter_by(id=id).first()
        return render_template("blog.html", blog=blog)
    if user_id:
        user = Blog.query.filter_by(owner_id=user_id).all()
        blogs = user
        return render_template("user.html", blogs=blogs)
    return render_template("blog_list.html", title="Build A Blog", blogs=blogs)

@app.route("/newpost", methods=["POST", "GET"])
def new_blog_post():
    owner = User.query.filter_by(username=session["user"]).first()
    title_error = ""
    body_error = ""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]    
        if title == "":
            title_error = "The blog cannot be nameless."
        if body == "":
            body_error = "A blog needs its meat. Give it some."
        if not title_error and not body_error:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id=" + str(new_blog.id))
    return render_template("new_blog.html", title="Add Blog Entry", title_error=title_error, body_error=body_error)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["user"] = username
            return redirect("/newpost")
        else:
            if not user:
                flash("User doesn't exist.", "error")
                username = ""
                return redirect("/login")
            else:
                flash("Password isn't correct.", "error")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]
        if username == "" or password == "":
            flash("please fill out all the fields.", "error")
            return redirect("/signup")
        else:
            if len(username) < 3:
                flash("username should be at least 3 characters long", "error")
                username = ""
                return redirect("/signup")
            elif len(password) < 3:
                flash("password should be at least 3 characters long", "error")
                return redirect("/signup")
            else:
                if verify != password:
                    flash("passwords do not match, password not verified", "error")
                    return redirect("/signup")
                existing_user = User.query.filter_by(username=username).first()
                if not existing_user:
                    new_user = User(username, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session["user"] = username
                    return redirect("/newpost")
                else:
                    flash("user already exists", "error")
                    username = ""
    return render_template("signup.html")

@app.route("/logout")
def logout():
    del session["user"]
    return redirect("/blog")

@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", title="Home", users=users)

allowed_routes = ["login", "blog_listings", "index", "signup"]

@app.before_request
def require_login():
    if not ("user" in session or request.endpoint in allowed_routes):
        return redirect("/login")

if __name__=="__main__":
    app.run()