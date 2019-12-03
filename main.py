from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://build-a-blog:jacoblog@localhost:3306/build-a-blog'
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog")
def blog_listings():
    blogs = Blog.query.all()
    id = request.args.get("id")
    if id:
        blog = Blog.query.filter_by(id=id).first()
        return render_template("blog.html", blog=blog)
    return render_template("blog_list.html", title="Build A Blog", blogs=blogs)

@app.route("/newpost", methods=["POST", "GET"])
def new_blog_post():
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
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id=" + str(new_blog.id))
    return render_template("new_blog.html", title="Add Blog Entry", title_error=title_error, body_error=body_error)

@app.route("/")
def index():
    return redirect("/blog")

if __name__=="__main__":
    app.run()