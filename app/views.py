from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, \
    login_required #for authentication
from flask.ext.user import roles_required #used for authorization
from sqlalchemy import desc
from app import app, db, lm, oid
from .forms import LoginForm, EditForm, PunchForm
from .models import User, Punch
from datetime import datetime



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request # functions decorated with before_request run before the view function when request is received
def before_request():
    g.user = current_user #g global is setup by Flask to store and share data during the life of a request
    #current_user global is set by Flask-Login; we put a copy in the g object so that all requests have access to the logged-in user, even inside templates
    if g.user.is_authenticated():
        db.session.add(g.user)
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required #require login before index access
def index():
    user = g.user
    punches = user.punches.order_by(desc(Punch.timestamp)).all()
    return render_template('user.html',
                           title='Home',
                           user=user,
                           punches=punches,
                           form = PunchForm())

#
#The login function
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler # tells Flask-OpenID that this is our login view function
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login #if the authentication is successful, Flask-OpenID calls this function
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))

#
#The logout function
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#
#Function to display user landing page after sign-in (the GET request) or allow a user to punch the clock (the POST request)
@app.route('/user/<nickname>', methods=['GET', 'POST']) 
@login_required 
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    form = PunchForm()
    if form.validate_on_submit():
        last_punch = user.punches.order_by(desc(Punch.timestamp))[0].in_or_out
        if last_punch == 'IN':
            this_punch = 'OUT'
        else:
            this_punch = 'IN'
        cp = Punch(timestamp=datetime.now(), in_or_out=this_punch, notes=form.notes.data, author=user)  
        db.session.add(cp)
        db.session.commit()
        flash('Your time has been recorded.')
        return redirect(url_for('user', nickname=g.user.nickname))
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    punches = user.punches.order_by(desc(Punch.timestamp))
    return render_template('user.html',
                           user=user,
                           punches=punches, 
                           form=form)

#
# The function that allows users to see (GET) their profile information, or edit (POST) it
@app.route('/edit', methods=['GET', 'POST']) #view that allows for a user to edit their profile info
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit(): #email purposefully left out
        g.user.nickname = form.nickname.data
        g.user.employee_number = form.employee_number.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', nickname=g.user.nickname))
    else:
        form.nickname.data = g.user.nickname
        form.email.data = g.user.email
        form.employee_number.data = g.user.employee_number
        flash('Your changes have not been saved, please check your input.')
    return render_template('edit.html', form=form)

#
# The function to view all clock-punches, with links to edit individual punches. Available only to managers
@app.route('/timereport') 
@login_required
def timereport():
    if g.user.is_manager:
        punches = Punch.query.order_by(desc(Punch.timestamp)).all()
        return render_template('report.html',
                           punches=punches)
    else:
        flash('You are not authorized to access this function.')
        return redirect(url_for('user', nickname=g.user.nickname))

#
# The function to view a particular clock-punch (GET), with option to edit (POST)
@app.route('/punch/<punchid>', methods=['GET', 'POST']) 
@login_required
def punch(punchid):
    if not g.user.is_manager:
        flash('You are not authorized to access this function.')
        return redirect(url_for('user', nickname=g.user.nickname))
    punch = Punch.query.get(punchid)
    form = PunchForm()
    if request.method == 'GET':
        form.notes.data = punch.notes
        form.timestamp.data = punch.timestamp
    if form.validate_on_submit():
        punch.notes = form.notes.data
        punch.timestamp = form.timestamp.data
        print(form.errors)
        db.session.commit()
        flash('Your changes have been saved.')
        return render_template('report.html', punches=Punch.query.order_by(desc(Punch.timestamp)).all())
    else:
        flash('Please check to see that you have entered information correctly.')
    return render_template('punch.html', form=form, punch=punch)

