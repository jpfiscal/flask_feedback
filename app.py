from flask import Flask, render_template, redirect, session, flash
# from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, addPostForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask-feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True

connect_db(app)
# with app.app_context:
#     db.create_all()

# toolbar = DebugToolbarExtension(app)

@app.route("/")
def homepage():
    """Route to registeration screen"""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    # """produce registeration form and handle form submission"""
    
    form = RegisterForm()

    if form.is_submitted() and form.validate():
        name = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        user = User.register(name,pwd,email,first_name,last_name)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.username

        return redirect(f"/users/{name}")
    else:
        return render_template("register.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Load login form and handle form submission for user login"""

    form = LoginForm()

    if form.is_submitted() and form.validate():
        name = form.username.data
        pwd = form.password.data

        user = User.authenticate(name,pwd)

        if user:
            session['user_id'] = user.username
            print(f"SESSION: {session['user_id']}")
            return redirect(f"/users/{name}")
        
        else:
                form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)
 
@app.route("/logout")
def logout():
     session.pop('user_id')
     flash("Goodbye!", "info")
     return redirect('/')

@app.route("/users/<username>")
def load_user(username):
     user = User.query.filter(User.username == username).first()
     feedback_list = user.feedbacks
     """load user details page"""
     if "user_id" not in session:
          flash("You must be logged in to view!")
          return redirect("/")
     else:
        logged_in_user = User.query.filter(User.username == session['user_id']).first()
        print(f"logged_in_user_id: {logged_in_user.id}")
        print(f"user: {user.id}")
        if session['user_id'] == user.username:
            return render_template("users.html", user=user, feedback_list = feedback_list)
        else:
            flash("You are not authorized to see this page!", "danger")
            return redirect("/")

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    user = User.query.filter(User.username == username).first()
    for feedback in user.feedbacks:
        db.session.delete(feedback)
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=["GET","POST"])
def add_post(username):
    form = addPostForm()

    if form.is_submitted() and form.validate():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{username}")
    else: 
        return render_template("add_feedback.html", username=username, form=form)
    

@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_post(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    print(feedback)
    username = feedback.username
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{username}")