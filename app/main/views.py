from datetime import datetime
from flask import render_template, session, redirect, url_for
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['know'] = False
            if app.config['FLASK_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.index'))
    return render_template('index.html',current_time=datetime.utcnow(),
                            name=session.get('name'),form=form,know=session.get('know',False))                                                      