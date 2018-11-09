from flask import Blueprint, render_template, request, flash
from stravalib import Client
from flask_login import current_user, LoginManager, login_required, confirm_login
from monolith.database import db, Run, Report
from monolith.forms import MailForm
from datetime import time

home = Blueprint('home', __name__)


def _strava_auth_url(config):
    client = Client()
    client_id = config['STRAVA_CLIENT_ID']
    redirect = 'http://127.0.0.1:5000/strava_auth'
    url = client.authorization_url(client_id=client_id,
                                   redirect_uri=redirect)
    return url


def strava_auth_url(config):
    return _strava_auth_url(config)


## In this case I don't specify the type required because:
## In the code there is the control of the current user
@home.route('/')
def index():
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        runs = db.session.query(Run).filter(Run.runner_id == current_user.id)
        total_average_speed = 0
        for run in runs:
            total_average_speed += run.average_speed
        if runs.count():
            total_average_speed /= runs.count()
        total_average_speed = round(total_average_speed, 2)
    else:
        runs = None
        total_average_speed = 0
    strava_auth_url = _strava_auth_url(home.app.config)
    return render_template("index.html", runs=runs,
                           strava_auth_url=strava_auth_url, total_average_speed=total_average_speed)

#In this we specify the setting for the management of the report
@home.route('/settingreport', methods=['GET', 'POST'])
@login_required
def settingreport():

    form = MailForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            mail = db.session.query(Report).filter(Report.id_user==current_user.id).first()  
            if mail is None:
                new_mail = Report()
                new_mail.set_user(current_user.id)
                new_mail.set_timestamp()
                option = request.form['setting_mail']
                if option is None:
                    flash('Select one category', category='error')
                    return make_response(render_template('mail.html', form=form), 401)
                else:
                    new_mail.set_decision(option) 
                    db.session.add(new_mail)
                    #print(new_mail)
                    #print(new_mail.id_user)
                    #print(new_mail.timestamp)
                    #print(new_mail.choice_time)
                    db.session.commit()
                    flash('Settings updated', category='success')
            else:
                mail.set_timestamp()
                option = request.form['setting_mail']
                if option is None:
                    flash('Select one category', category='error')
                    return make_response(render_template('mail.html', form=form), 401)
                else:
                    mail.set_decision(option)
                    db.session.merge(mail)
                    #print(mail)
                    #print(mail.id_user)
                    #print(mail.timestamp)
                    #print(mail.choice_time)
                    db.session.commit()
                    flash('Settings updated', category='success')
    return render_template('mail.html', form=form)