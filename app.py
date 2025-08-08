from flask import Flask, render_template, request
from markupsafe import Markup
from flask_socketio import SocketIO
from flask_cors import CORS
from model.fixture_up_down import get_today_fixtures_db
from model.db import sqlite_connection
from model.entities import FixtureQueue, load_default_fixture_queue
from threading import Thread
from queue import Queue
#from model.fetch_fixtures import fetch_fixtures_json

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

#turn the flask app into a socketio app
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_orgins="*")

# #start threads
# db_thread = None
# dbqueue = Queue()
# stop = False

# #db = db_connection()
db = sqlite_connection()

# #db = db_connection()
# db = sqlite_connection()
cursorB = db.cursor()

# def dbconsumer():
#     # Create an infinite loop
#     while not stop:
#         try:
#             # Attempt to get data from the queue. Note that
#             # dataQueue.get() will block this thread's execution
#             # until data is available
#             cursor, stmt = dbqueue.get()
#             cursor.execute(stmt)
#             db.commit()
#         except:
#             pass

fixture_queue_B = load_default_fixture_queue()

# def render_squadi_timer():
#     fixtures = fetch_fixtures_json()
#     return render_template('squadi-timer.html')


"""
RENDER HTML TEMPLATES
"""
def render_scoreboard(fixture_queue: FixtureQueue, court, iscopy: bool):
    home_teams = set()
    away_teams = set()
    homeLogoHtml = '<img id="defaultHomeLogo" class="logo" src="/static/img/ipswich-futsal-rgb.png">'
    awayLogoHtml = f'<img id="defaultAwayLogo" class="logo" src="/static/img/sala-time.png">'
    for fixture in fixture_queue.remaining_fixtures():
        home_team = fixture.get_home_team()
        home_id = home_team.get_id()
        away_team = fixture.get_away_team()
        away_id = away_team.get_id()
        if home_team.get_logo() != None and home_id not in home_teams:
            homeLogoHtml = homeLogoHtml + '\n' + f'<img id="homeLogo{home_team.get_id()}" class="logo display-none" src="/static/img/{home_team.get_logo()}.png">'
            home_teams.add(home_id)
        if away_team.get_logo() != None and away_id not in away_teams:
            awayLogoHtml = awayLogoHtml + '\n' + f'<img id="awayLogo{away_team.get_id()}" class="logo display-none" src="/static/img/{away_team.get_logo()}.png">'
            away_teams.add(away_id)
    homeLogoHtml = Markup(homeLogoHtml)
    awayLogoHtml = Markup(awayLogoHtml)
    script = '<script src="/static/js/scoreboard-script.js"></script>'
    if iscopy:
        script = '<script src="/static/js/scoreboard-copy-script.js"></script>'
    script = Markup(script)
    return render_template('scoreboard.html', script=script, court=court, 
            homeLogo=homeLogoHtml, awayLogo=awayLogoHtml,
            period = fixture_queue.get_current_fixture().get_current_period().get_display_name(),
            homeName = fixture_queue.get_current_fixture().get_home_team().get_name(),
            awayName = fixture_queue.get_current_fixture().get_away_team().get_name(),
            homeGoals = fixture_queue.get_current_fixture().get_home_score(),
            awayGoals = fixture_queue.get_current_fixture().get_away_score(),
            homeFouls = fixture_queue.get_current_fixture().get_home_fouls(),
            awayFouls = fixture_queue.get_current_fixture().get_away_fouls()
    )

@app.route('/courtB')
def courtB():
    return render_scoreboard(fixture_queue_B, "B", iscopy=False)

# @app.route('/courtBcopy')
# def courtBcopy():
#     return render_scoreboard(fixture_queue_B, "B", iscopy=True)

def render_ticker(fixture_queue: FixtureQueue, court):
    return render_template('ticker.html', court=court,
            homeColour = fixture_queue.get_current_fixture().get_home_team().get_colour(),
            awayColour = fixture_queue.get_current_fixture().get_away_team().get_colour(),
            homeAbbrev = fixture_queue.get_current_fixture().get_home_team().get_abbreviation(),
            awayAbbrev = fixture_queue.get_current_fixture().get_away_team().get_abbreviation(),
            homeGoals = fixture_queue.get_current_fixture().get_home_score(),
            awayGoals = fixture_queue.get_current_fixture().get_away_score()
    )

# @app.route('/courtBticker')
# def courtBticker():
#     return render_ticker(fixture_queue_B, "B")

@app.route('/remoteB')
def remoteB():
    return render_template('controller.html', court="B")

@app.route('/homescoreB')
def homescoreB():
    return render_template('homescore.html')

@app.route('/awayscoreB')
def awayscoreB():
    return render_template('awayscore.html')

@app.route('/alonetimerB')
def alonetimerB():
    return render_template('alonetimer.html')

@app.route('/extendedRemoteB')
def extendedRemoteB():
    return render_extended_controller(fixture_queue_B)

def render_extended_controller(fixture_queue: FixtureQueue):
    return render_template('extended_controller.html', 
                            homeName = fixture_queue.get_current_fixture().get_home_team().get_name(),
                            awayName = fixture_queue.get_current_fixture().get_away_team().get_name(),
                            homeAbbrev = fixture_queue.get_current_fixture().get_home_team().get_abbreviation(),
                            awayAbbrev = fixture_queue.get_current_fixture().get_away_team().get_abbreviation()
    )

@app.route('/upload-home-logo', methods=['POST'])
def upload_home_logo():
    if 'homeLogo' in request.files:
        home_logo = request.files['homeLogo']
        if home_logo.filename != '':
            home_logo.save(f'static/img/{fixture_queue_B.get_current_fixture().get_home_team().get_name()}-logo.png')
            fixture_queue_B.get_current_fixture().get_home_team().set_logo(f'{fixture_queue_B.get_current_fixture().get_home_team().get_name()}-logo')

            # Update the home logo in the scoreboard
            socketio.emit('changehomelogo', {'url': f'/static/img/{fixture_queue_B.get_current_fixture().get_home_team().get_name()}-logo.png'}, namespace="/courtB")
    
    return ""


@app.route('/upload-away-logo', methods=['POST'])
def upload_away_logo():
    if 'awayLogo' in request.files:
        away_logo = request.files['awayLogo']
        if away_logo.filename != '':
            away_logo.save(f'static/img/{fixture_queue_B.get_current_fixture().get_away_team().get_name()}-logo.png')
            fixture_queue_B.get_current_fixture().get_away_team().set_logo(f'{fixture_queue_B.get_current_fixture().get_away_team().get_name()}-logo')

            # Update the away logo in the scoreboard
            socketio.emit('changeawaylogo', {'url': f'/static/img/{fixture_queue_B.get_current_fixture().get_away_team().get_name()}-logo.png'}, namespace="/courtB")

    return ""

# @app.route('/extendedRemoteB', methods=['POST'])
# def upload_logos():
#     if 'homeLogo' in request.files:
#         home_logo = request.files['homeLogo']
#         if home_logo.filename != '':
#             home_logo.save(f'static/img/{fixture_queue_B.get_current_fixture().get_home_team().get_id()}-logo.png')
#             fixture_queue_B.get_current_fixture().get_home_team().set_logo(f'{fixture_queue_B.get_current_fixture().get_home_team().get_id()}-logo')
#     if 'awayLogo' in request.files:
#         away_logo = request.files['awayLogo']
#         if away_logo.filename != '':
#             away_logo.save(f'static/img/{fixture_queue_B.get_current_fixture().get_away_team().get_id()}-logo.png')
#             fixture_queue_B.get_current_fixture().get_away_team().set_logo(f'{fixture_queue_B.get_current_fixture().get_away_team().get_id()}-logo')
#     return render_extended_controller(fixture_queue_B)

"""
CONNECTION SOCKET EVENTS
"""
@socketio.on('connect', namespace="/courtB")
def handle_connection_B():
    print('scoreboard B has connected')
    if fixture_queue_B.ticker_connected():
       socketio.emit('tickerconnected', namespace="/courtB")
    if fixture_queue_B.copy_connected():
           socketio.emit('copyconnected', namespace="/courtB")
    socketio.emit('fixturequeue', fixture_queue_B.get_json(), namespace="/courtB")

@socketio.on('connect', namespace="/courtBcopy")
def handle_connection_Bcopy():
    print('scoreboard copy B has connected')
    fixture_queue_B.set_copy_connected(True)
    socketio.emit('copyconnected', namespace="/courtB")
    socketio.emit('firstcopyfixture', namespace="/courtB")

@socketio.on('connect', namespace="/courtBticker")
def handle_connection_Btick():
    print('ticker B has connected')
    fixture_queue_B.set_ticker_connected(True)
    socketio.emit('tickerconnected', namespace="/courtB")
    #socketio.emit('fixturequeue', fixture_queue_B.get_json(), namespace="/courtBticker")

@socketio.on('connect', namespace="/remoteB")
def handle_connection_remoteB():
    print('remote B connected')
    socketio.emit('getpausestatus', namespace="/courtB")

@socketio.on('connect', namespace="/extendedRemoteB")
def handle_connection_remoteB():
    print('remote B connected')
    socketio.emit('getpausestatus', namespace="/courtB")
    socketio.emit('extendedremoteconnected', namespace="/courtB")

@socketio.on('connect', namespace="/homescoreB")
def handle_connect_homescore_B():
    print('homescore B connected')

@socketio.on('connect', namespace="/awayscoreB")
def handle_connect_homescore_B():
    print('awayscore B connected')

@socketio.on('connect', namespace="/alonetimerB")
def handle_connect_alonetimer_B():
    print('alonetimer B connected')
    fixture_queue_B.set_alonetimer_connected(True)
    socketio.emit('alonetimerconnected', namespace="/courtB")

@socketio.on('connect', namespace="/homescoreB")
def handle_connect_homescore_B():
    print('homescore B connected')

@socketio.on('connect', namespace="/awayscoreB")
def handle_connect_homescore_B():
    print('awayscore B connected')

@socketio.on('connect', namespace="/alonetimerB")
def handle_connect_alonetimer_B():
    print('alonetimer B connected')
    fixture_queue_B.set_alonetimer_connected(True)
    socketio.emit('alonetimerconnected', namespace="/courtB")

@socketio.on('pausestatus', namespace="/courtB")
def set_remoteB_pause_status(paused):
    socketio.emit('pausestatus', paused, namespace="/remoteB")
    socketio.emit('pausestatus', paused, namespace="/extendedRemoteB")

"""
TIMER AND FIXTURE UPDATE EVENTS FOR TICKER AND SCOREBOARD COPY
"""
@socketio.on('ertimer', namespace="/courtB")
def timer_er_B(timer):
    socketio.emit('ertimer', timer, namespace="/extendedRemoteB")

@socketio.on('tickertimer', namespace="/courtB")
def timer_ticker_B(timer):
    socketio.emit('tickertimer', timer, namespace=f"/courtBticker")

@socketio.on('copytimer', namespace="/courtB")
def timer_copy_B(timer):
    socketio.emit('copytimer', timer, namespace=f"/courtBcopy")

@socketio.on('alonetimer', namespace="/courtB")
def timer_alone_B(timer):
    socketio.emit('alonetimer', timer, namespace="/alonetimerB")

def new_fixture_slaves(fixture_queue: FixtureQueue, new_fixture, crt):
    fixture_queue.next_fixture()
    #socketio.emit('nextfixture', namespace=f"/court{crt}ticker")
    #socketio.emit('nextfixture', new_fixture, namespace=f"/court{crt}copy") 
    socketio.emit('nextfixture', namespace=f"/alonetimer{crt}") 
    socketio.emit('nextfixture', namespace=f"/homescore{crt}") 
    socketio.emit('nextfixture', namespace=f"/awayscore{crt}") 
    # socketio.emit('nextfixture', namespace=f"/alonetimer{crt}") 
    # socketio.emit('nextfixture', namespace=f"/homescore{crt}") 
    # socketio.emit('nextfixture', namespace=f"/awayscore{crt}") 

@socketio.on('newfixture', namespace="/courtB")
def new_fixture_ticker_B(new_fixture):
    new_fixture_slaves(fixture_queue_B, new_fixture, "B")

# @socketio.on('firstfixture', namespace="/courtB")
# def first_fixture_copy_B(current_fixture):
#     socketio.emit('firstfixture', current_fixture, namespace="/courtBcopy")

@socketio.on('updateperiod', namespace="/courtB")
def update_period_copy_B(period):
    fixture_queue_B.get_current_fixture().set_current_period(period['sortOrder'])
    #socketio.emit('updateperiod', period['displayName'], namespace="/courtBcopy")
    socketio.emit('updateperiod', period['displayName'], namespace="/extendedRemoteB")

# @socketio.on('playsiren', namespace="/courtB")
# def play_siren_copy_B():
#     socketio.emit('playsiren', namespace="/courtBcopy")

@socketio.on('showtimeticker', namespace="/courtB")
def show_time_ticker_B():
    #socketio.emit('showtimer', namespace="/courtBticker")
    socketio.emit('showtimer', namespace="/alonetimerB")

"""
HANDLE GOALS, FOULS AND PENALTY SHOOTOUTS.
"""
def handle_score_update(fixture_queue: FixtureQueue, cursor, crt, update):
    if 'homeGoals' in update:
        fixture_queue.get_current_fixture().set_home_score(update['homeGoals'])
        #dbqueue.put((cursor, f"UPDATE fixtures SET home_score = {update['homeGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}ticker")
        #socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}copy")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/homescore{crt}")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/homescore{crt}")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/extendedRemote{crt}")
    else:
        fixture_queue.get_current_fixture().set_away_score(update['awayGoals'])
        #dbqueue.put((cursor, f"UPDATE fixtures SET away_score = {update['awayGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}ticker")
        #socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}copy")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/awayscore{crt}")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/awayscore{crt}")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/extendedRemote{crt}")

@socketio.on('score', namespace="/courtB")
def score_B(update):
    handle_score_update(fixture_queue_B, cursorB, "B", update)

def handle_foul_update(fixture_queue: FixtureQueue, crt, update):
    if 'homeFouls' in update:
        fixture_queue.get_current_fixture().set_home_fouls(update['homeFouls'])
        #socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/court{crt}copy")
        socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/extendedRemote{crt}")
    else:
        fixture_queue.get_current_fixture().set_away_fouls(update['awayFouls'])
        #socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/court{crt}copy")
        socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/extendedRemote{crt}")

@socketio.on('foul', namespace="/courtB")
def foul_B(update):
    handle_foul_update(fixture_queue_B, "B", update)

def handle_went_penalties(fixture_queue: FixtureQueue, crt):
    fixture_queue.get_current_fixture().set_went_penalties(True)
    socketio.emit("wentpenalties", namespace=f"/court{crt}ticker")

@socketio.on('wentpenalties', namespace="/courtB")
def went_penalties_B():
    handle_went_penalties(fixture_queue_B, "B")

def handle_penalty_update(fixture_queue: FixtureQueue, cursor, crt, update):
    if 'homePenalties' in update:
        fixture_queue.get_current_fixture().set_home_penalties(update['homePenalties'])
        #dbqueue.put((cursor, f"UPDATE fixtures SET home_penalties = {sum(update['homePenalties'])} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        fixture_queue.get_current_fixture().set_home_penalties_left(update['homePenaltiesLeft'])
        socketio.emit('homepenaltyupdate', update['homePenalties'], namespace=f"/court{crt}ticker")
    else:
        fixture_queue.get_current_fixture().set_away_penalties(update['awayPenalties'])
        #dbqueue.put((cursor, f"UPDATE fixtures SET away_penalties = {sum(update['awayPenalties'])} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        fixture_queue.get_current_fixture().set_away_penalties_left(update['awayPenaltiesLeft'])
        socketio.emit('awaypenaltyupdate', update['awayPenalties'], namespace=f"/court{crt}ticker")

@socketio.on('penalty', namespace="/courtB")
def penalty_B(update):
    handle_penalty_update(fixture_queue_B, cursorB, "B", update)

def handle_sudden_death(fixture_queue: FixtureQueue, crt):
    fixture_queue.get_current_fixture().set_home_penalties_left(1)
    fixture_queue.get_current_fixture().set_away_penalties_left(1)
    socketio.emit('suddendeath', namespace=f"/court{crt}ticker")

@socketio.on('suddendeath', namespace="/courtB")
def sudden_death_B():
    handle_sudden_death(fixture_queue_B, "B")

"""
SCORE AND FOUL FOR WEB REMOTES
"""
def handle_remote_score_update(fixture_queue: FixtureQueue, cursor, crt, update):
    if update == 'homeGoalIncrement':
        fixture_queue.get_current_fixture().add_home_score(1)
        socketio.emit('homegoaladd', namespace=f"/court{crt}")
        #dbqueue.put((cursor, f"UPDATE fixtures SET home_score = home_score + 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('homegoaladd', namespace=f"/court{crt}ticker")
        #socketio.emit('homegoaladd', namespace=f"/court{crt}copy")
        socketio.emit('homegoaladd', namespace=f"/extendedRemote{crt}")
    elif update == 'awayGoalIncrement':
        fixture_queue.get_current_fixture().add_away_score(1)
        socketio.emit('awaygoaladd', namespace=f"/court{crt}")
        #dbqueue.put((cursor, f"UPDATE fixtures SET away_score = away_score + 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('awaygoaladd', namespace=f"/court{crt}ticker")
        #socketio.emit('awaygoaladd', namespace=f"/court{crt}copy")
        socketio.emit('awaygoaladd', namespace=f"/extendedRemote{crt}")
    elif update == 'homeGoalDecrement':
        fixture_queue.get_current_fixture().add_home_score(-1)
        socketio.emit('homegoaltake', namespace=f"/court{crt}")
        #dbqueue.put((cursor, f"UPDATE fixtures SET home_score = home_score - 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('homegoaltake', namespace=f"/court{crt}ticker")
        #socketio.emit('homegoaltake', namespace=f"/court{crt}copy")
        socketio.emit('homegoaltake', namespace=f"/extendedRemote{crt}")
    elif update == 'awayGoalDecrement':
        fixture_queue.get_current_fixture().add_away_score(-1)
        socketio.emit('awaygoaltake', namespace=f"/court{crt}")
        #dbqueue.put((cursor, f"UPDATE fixtures SET away_score = away_score - 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('awaygoaltake', namespace=f"/court{crt}ticker")
        #socketio.emit('awaygoaltake', namespace=f"/court{crt}copy")
        socketio.emit('awaygoaltake', namespace=f"/extendedRemote{crt}")
    elif 'homeGoals' in update:
        fixture_queue.get_current_fixture().set_home_score(update['homeGoals'])
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}")
        #dbqueue.put((cursor, f"UPDATE fixtures SET home_score = {update['homeGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}ticker")
        #socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}copy")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/extendedRemote{crt}")
    elif 'awayGoals' in update:
        fixture_queue.get_current_fixture().set_away_score(update['awayGoals'])
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}")
        #dbqueue.put((cursor, f"UPDATE fixtures SET away_score = {update['awayGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        #socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}ticker")
        #socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}copy")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/extendedRemote{crt}")

def handle_remote_foul_update(fixture_queue: FixtureQueue, crt, update):
    if update == 'homeFoulIncrement':
        fixture_queue.get_current_fixture().add_home_fouls(1)
        socketio.emit('homefouladd', namespace=f"/court{crt}")
        #socketio.emit('homefouladd', namespace=f"/court{crt}copy")
        socketio.emit('homefouladd', namespace=f"/extendedRemote{crt}")
    elif update == 'awayFoulIncrement':
        fixture_queue.get_current_fixture().add_away_fouls(1)
        socketio.emit('awayfouladd', namespace=f"/court{crt}")
        #socketio.emit('awayfouladd', namespace=f"/court{crt}copy")
        socketio.emit('awayfouladd', namespace=f"/extendedRemote{crt}")
    elif update == 'homeFoulDecrement':
        fixture_queue.get_current_fixture().add_home_fouls(-1)
        socketio.emit('homefoultake', namespace=f"/court{crt}")
        #socketio.emit('homefoultake', namespace=f"/court{crt}copy")
        socketio.emit('homefoultake', namespace=f"/extendedRemote{crt}")
    elif update == 'awayFoulDecrement':
        fixture_queue.get_current_fixture().add_away_fouls(-1)
        socketio.emit('awayfoultake', namespace=f"/court{crt}")
        #socketio.emit('awayfoultake', namespace=f"/court{crt}copy")
        socketio.emit('awayfoultake', namespace=f"/extendedRemote{crt}")
    elif 'homeFouls' in update:
        fixture_queue.get_current_fixture().set_home_fouls(update['homeFouls'])
        socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/court{crt}")
        #socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/court{crt}copy")
        socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/extendedRemote{crt}")
    elif 'awayFouls' in update:
        fixture_queue.get_current_fixture().set_away_fouls(update['awayFouls'])
        socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/court{crt}")
        #socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/court{crt}copy")
        socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/extendedRemote{crt}")

@socketio.on('score', namespace="/remoteB")
def remote_score_B(update):
    handle_remote_score_update(fixture_queue_B, cursorB, "B", update)

@socketio.on('score', namespace="/extendedRemoteB")
def extended_remote_score_B(update):
    handle_remote_score_update(fixture_queue_B, cursorB, "B", update)

@socketio.on('foul', namespace="/remoteB")
def remote_foul_B(update):
    handle_remote_foul_update(fixture_queue_B, "B", update)

@socketio.on('foul', namespace="/extendedRemoteB")
def extended_remote_foul_B(update):
    handle_remote_foul_update(fixture_queue_B, "B", update)

@socketio.on('pause', namespace="/remoteB")
def pause_court_B():
    socketio.emit('pause', namespace="/courtB")

@socketio.on('pause', namespace="/extendedRemoteB")
def pause_court_B():
    socketio.emit('pause', namespace="/courtB")

@socketio.on('resume', namespace="/remoteB")
def resume_court_B():
    socketio.emit('resume', namespace="/courtB")

@socketio.on('resume', namespace="/extendedRemoteB")
def resume_court_B():
    socketio.emit('resume', namespace="/courtB")

@socketio.on('sirenloop', namespace="/remoteB")
def siren_loop_B():
    socketio.emit('sirenloop', namespace="/courtB")

@socketio.on('endsirenloop', namespace="/remoteB")
def end_siren_loop_B():
    socketio.emit('endsirenloop', namespace="/courtB")

@socketio.on('siren', namespace="/remoteB")
def siren_B():
    socketio.emit('siren', namespace="/courtB")

@socketio.on('siren', namespace="/extendedRemoteB")
def siren_B():
    socketio.emit('siren', namespace="/courtB")

@socketio.on('delay', namespace="/remoteB")
def delay_court_B(time):
    fixture_queue_B.move_fixture_times(time)
    socketio.emit('delay', time, namespace="/courtB")

@socketio.on('delay', namespace="/extendedRemoteB")
def delay_court_B(time):
    fixture_queue_B.move_fixture_times(time)
    socketio.emit('delay', time, namespace="/courtB")

@socketio.on('bringforward', namespace="/remoteB")
def bring_forward_court_B(time):
    fixture_queue_B.move_fixture_times(-time)
    socketio.emit('bringforward', time, namespace="/courtB")

@socketio.on('bringforward', namespace="/extendedRemoteB")
def bring_forward_court_B(time):
    fixture_queue_B.move_fixture_times(-time)
    socketio.emit('bringforward', time, namespace="/courtB")

@socketio.on('startperiod', namespace="/remoteB")
def start_period_B():
    socketio.emit('startperiod', namespace="/courtB")

@socketio.on('startperiod', namespace="/extendedRemoteB")
def start_period_B():
    socketio.emit('startperiod', namespace="/courtB")

@socketio.on('startnextgame', namespace="/remoteB")
def start_game_B():
    socketio.emit('startnextgame', namespace="/courtB")

@socketio.on('restartgame', namespace="/extendedRemoteB")
def restart_game_B():
    socketio.emit('restartgame', namespace="/courtB")

@socketio.on('restartperiod', namespace="/extendedRemoteB")
def restart_period_B():
    socketio.emit('restartperiod', namespace="/courtB")

@socketio.on('previousperiod', namespace="/extendedRemoteB")
def previous_period_B():
    socketio.emit('previousperiod', namespace="/courtB")

@socketio.on('nextperiod', namespace="/extendedRemoteB")
def next_period_B():
    socketio.emit('nextperiod', namespace="/courtB")

@socketio.on('previousgame', namespace="/extendedRemoteB")
def previous_game_B():
    socketio.emit('previousgame', namespace="/courtB")

@socketio.on('startnextgame', namespace="/extendedRemoteB")
def next_game_B():
    socketio.emit('startnextgame', namespace="/courtB")

@socketio.on('timeout', namespace='/extendedRemoteB')
def timeout():
    socketio.emit('timeout', namespace="/courtB")

@socketio.on('canceltimeout', namespace='/extendedRemoteB')
def cancel_timeout():
    socketio.emit('canceltimeout', namespace="/courtB")

@socketio.on('timeoutover', namespace='/courtB')
def timeoutover():
    socketio.emit('timeoutover', namespace="/extendedRemoteB")

# Edit team atttributes
@socketio.on('changehomename', namespace="/extendedRemoteB")
def change_home_name(name):
    fixture_queue_B.get_current_fixture().get_home_team().set_name(name)
    socketio.emit('changehomename', name, namespace="/courtB")
    socketio.emit('changehomename', name, namespace="/extendedRemoteB")

@socketio.on('changeawayname', namespace="/extendedRemoteB")
def change_away_name(name):
    fixture_queue_B.get_current_fixture().get_away_team().set_name(name)
    socketio.emit('changeawayname', name, namespace="/courtB")
    socketio.emit('changeawayname', name, namespace="/extendedRemoteB")

@socketio.on('changehomeabbrev', namespace="/extendedRemoteB")
def change_home_abbrev(abbrev):
    fixture_queue_B.get_current_fixture().get_home_team().set_abbreviation(abbrev)
    #socketio.emit('changehomeabbrev', abbrev, namespace="/courtBticker")
    socketio.emit('changehomeabbrev', abbrev, namespace="/extendedRemoteB")

@socketio.on('changeawayabbrev', namespace="/extendedRemoteB")
def change_away_abbrev(abbrev):
    fixture_queue_B.get_current_fixture().get_away_team().set_abbreviation(abbrev)
    #socketio.emit('changeawayabbrev', abbrev, namespace="/courtBticker")
    socketio.emit('changeawayabbrev', abbrev, namespace="/extendedRemoteB")

@socketio.on('changehomecolour', namespace="/extendedRemoteB")
def change_home_colour(colour):
    fixture_queue_B.get_current_fixture().get_home_team().set_colour(colour)
    socketio.emit('changehomecolour', colour, namespace="/courtBticker")

@socketio.on('changeawaycolour', namespace="/extendedRemoteB")
def change_away_colour(colour):
    fixture_queue_B.get_current_fixture().get_away_team().set_colour(colour)
    socketio.emit('changeawaycolour', colour, namespace="/courtBticker")

@socketio.on('disconnect')
def disconnect():
    pass

if __name__ == '__main__':
    # if db_thread is None:
    #     db_thread = Thread(target=dbconsumer)
    #     db_thread.daemon = True
    #     db_thread.start()
    socketio.run(app, host="0.0.0.0", port=80)
# else:
#     cursorB.close()
#     db.close()