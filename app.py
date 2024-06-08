from flask import Flask, render_template, request
from markupsafe import Markup
from flask_socketio import SocketIO
from flask_cors import CORS
from model.fixture_up_down import get_today_fixtures_db
from model.db import sqlite_connection
from model.entities import FixtureQueue
from threading import Thread
from queue import Queue

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

#turn the flask app into a socketio app
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_orgins="*")

#start threads
db_thread = None
dbqueue = Queue()
stop = False

#db = db_connection()
db = sqlite_connection()

#db = db_connection()
db = sqlite_connection()
cursorA = db.cursor()
cursorB = db.cursor()
fixture_queue_A = get_today_fixtures_db(cursorA, "Ripley Valley SSC - Court A")
fixture_queue_B = get_today_fixtures_db(cursorB, "Ripley Valley SSC - Court B")
courtAfinished = False
courtBfinished = False

def dbconsumer():
    # Create an infinite loop
    while not stop:
        try:
            # Attempt to get data from the queue. Note that
            # dataQueue.get() will block this thread's execution
            # until data is available
            cursor, stmt = dbqueue.get()
            cursor.execute(stmt)
            db.commit()
        except:
            pass

"""
RENDER HTML TEMPLATES
"""
def render_scoreboard(fixture_queue: FixtureQueue, court, iscopy: bool):
    home_teams = set()
    away_teams = set()
    homeLogoHtml = '<img id="defaultHomeLogo" class="logo" src="/static/img/ipswich-futsal-rgb.png">'
    awayLogoHtml = f'<img id="defaultAwayLogo" class="logo" src="/static/img/ipswich-futsal-rgb.png">'
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

@app.route('/courtA')
def courtA():
    return render_scoreboard(fixture_queue_A, "A", iscopy=False)

@app.route('/courtB')
def courtB():
    return render_scoreboard(fixture_queue_B, "B", iscopy=False)

@app.route('/courtAcopy')
def courtAcopy():
    return render_scoreboard(fixture_queue_A, "A", iscopy=True)

@app.route('/courtBcopy')
def courtBcopy():
    return render_scoreboard(fixture_queue_B, "B", iscopy=True)

def render_ticker(fixture_queue: FixtureQueue, court):
    return render_template('ticker.html', court=court,
            homeColour = fixture_queue.get_current_fixture().get_home_team().get_colour(),
            awayColour = fixture_queue.get_current_fixture().get_away_team().get_colour(),
            homeAbbrev = fixture_queue.get_current_fixture().get_home_team().get_abbreviation(),
            awayAbbrev = fixture_queue.get_current_fixture().get_away_team().get_abbreviation(),
            homeGoals = fixture_queue.get_current_fixture().get_home_score(),
            awayGoals = fixture_queue.get_current_fixture().get_away_score()
    )

@app.route('/courtAticker')
def courtAticker():
    return render_ticker(fixture_queue_A, "A")

@app.route('/courtBticker')
def courtBticker():
    return render_ticker(fixture_queue_B, "B")

@app.route('/remoteA')
def remoteA():
    return render_template('controller.html', court="A")

@app.route('/remoteB')
def remoteB():
    return render_template('controller.html', court="B")

@app.route('/homescoreA')
def homescoreA():
    return render_template('homescore.html')

@app.route('/awayscoreA')
def awayscoreA():
    return render_template('awayscore.html')

@app.route('/homescoreB')
def homescoreB():
    return render_template('homescore.html')

@app.route('/awayscoreB')
def awayscoreB():
    return render_template('awayscore.html')

@app.route('/alonetimerA')
def alonetimerA():
    return render_template('alonetimer.html')

@app.route('/alonetimerB')
def alonetimerB():
    return render_template('alonetimer.html')


"""
CONNECTION SOCKET EVENTS
"""
@socketio.on('connect', namespace="/courtA")
def handle_connection_A():
    print('scoreboard A has connected')
    if fixture_queue_A.ticker_connected():
        socketio.emit('tickerconnected', namespace="/courtA")
    if fixture_queue_A.copy_connected():
            socketio.emit('copyconnected', namespace="/courtA")
    socketio.emit('fixturequeue', fixture_queue_A.get_json(), namespace="/courtA")

@socketio.on('connect', namespace="/courtB")
def handle_connection_B():
    print('scoreboard B has connected')
    if fixture_queue_B.ticker_connected():
        socketio.emit('tickerconnected', namespace="/courtB")
    if fixture_queue_B.copy_connected():
            socketio.emit('copyconnected', namespace="/courtB")
    socketio.emit('fixturequeue', fixture_queue_B.get_json(), namespace="/courtB")

@socketio.on('connect', namespace="/courtAcopy")
def handle_connection_Acopy():
    print('scoreboard copy A has connected')
    fixture_queue_A.set_copy_connected(True)
    socketio.emit('copyconnected', namespace="/courtA")
    socketio.emit('firstcopyfixture', namespace="/courtA")

@socketio.on('connect', namespace="/courtBcopy")
def handle_connection_Bcopy():
    print('scoreboard copy B has connected')
    fixture_queue_B.set_copy_connected(True)
    socketio.emit('copyconnected', namespace="/courtB")
    socketio.emit('firstcopyfixture', namespace="/courtB")

@socketio.on('connect', namespace="/courtAticker")
def handle_connection_Atick():
    print('ticker A has connected')
    fixture_queue_A.set_ticker_connected(True)
    socketio.emit('tickerconnected', namespace="/courtA")
    socketio.emit('fixturequeue', fixture_queue_A.get_json(), namespace="/courtAticker")

@socketio.on('connect', namespace="/courtBticker")
def handle_connection_Btick():
    print('ticker B has connected')
    fixture_queue_B.set_ticker_connected(True)
    socketio.emit('tickerconnected', namespace="/courtB")
    socketio.emit('fixturequeue', fixture_queue_B.get_json(), namespace="/courtBticker")

@socketio.on('connect', namespace="/remoteA")
def handle_connection_remoteA():
    print('remote A connected')
    socketio.emit('getpausestatus', namespace="/courtA")

@socketio.on('connect', namespace="/remoteB")
def handle_connection_remoteB():
    print('remote B connected')
    socketio.emit('getpausestatus', namespace="/courtB")

@socketio.on('connect', namespace="/homescoreA")
def handle_connect_homescore_A():
    print('homescore A connected')

@socketio.on('connect', namespace="/homescoreB")
def handle_connect_homescore_B():
    print('homescore B connected')

@socketio.on('connect', namespace="/awayscoreA")
def handle_connect_homescore_A():
    print('awayscore A connected')

@socketio.on('connect', namespace="/awayscoreB")
def handle_connect_homescore_B():
    print('awayscore B connected')

@socketio.on('connect', namespace="/alonetimerA")
def handle_connect_alonetimer_A():
    print('alonetimer A connected')
    fixture_queue_A.set_alonetimer_connected(True)
    socketio.emit('alonetimerconnected', namespace="/courtA")

@socketio.on('connect', namespace="/alonetimerB")
def handle_connect_alonetimer_B():
    print('alonetimer B connected')
    fixture_queue_B.set_alonetimer_connected(True)
    socketio.emit('alonetimerconnected', namespace="/courtB")

@socketio.on('connect', namespace="/homescoreA")
def handle_connect_homescore_A():
    print('homescore A connected')

@socketio.on('connect', namespace="/homescoreB")
def handle_connect_homescore_B():
    print('homescore B connected')

@socketio.on('connect', namespace="/awayscoreA")
def handle_connect_homescore_A():
    print('awayscore A connected')

@socketio.on('connect', namespace="/awayscoreB")
def handle_connect_homescore_B():
    print('awayscore B connected')

@socketio.on('connect', namespace="/alonetimerA")
def handle_connect_alonetimer_A():
    print('alonetimer A connected')
    fixture_queue_A.set_alonetimer_connected(True)
    socketio.emit('alonetimerconnected', namespace="/courtA")

@socketio.on('connect', namespace="/alonetimerB")
def handle_connect_alonetimer_B():
    print('alonetimer B connected')
    fixture_queue_B.set_alonetimer_connected(True)
    socketio.emit('alonetimerconnected', namespace="/courtB")

@socketio.on('pausestatus', namespace="/courtA")
def set_remoteA_pause_status(paused):
    socketio.emit('pausestatus', paused, namespace="/remoteA")

@socketio.on('pausestatus', namespace="/courtB")
def set_remoteB_pause_status(paused):
    socketio.emit('pausestatus', paused, namespace="/remoteB")

"""
TIMER AND FIXTURE UPDATE EVENTS FOR TICKER AND SCOREBOARD COPY
"""
@socketio.on('tickertimer', namespace="/courtA")
def timer_ticker_A(timer):
    socketio.emit('tickertimer', timer, namespace=f"/courtAticker")

@socketio.on('tickertimer', namespace="/courtB")
def timer_ticker_B(timer):
    socketio.emit('tickertimer', timer, namespace=f"/courtBticker")

@socketio.on('copytimer', namespace="/courtA")
def timer_copy_A(timer):
    socketio.emit('copytimer', timer, namespace=f"/courtAcopy")

@socketio.on('copytimer', namespace="/courtB")
def timer_copy_B(timer):
    socketio.emit('copytimer', timer, namespace=f"/courtBcopy")

@socketio.on('alonetimer', namespace="/courtA")
def timer_alone_A(timer):
    socketio.emit('alonetimer', timer, namespace="/alonetimerA")

@socketio.on('alonetimer', namespace="/courtB")
def timer_alone_B(timer):
    socketio.emit('alonetimer', timer, namespace="/alonetimerB")

@socketio.on('alonetimer', namespace="/courtA")
def timer_alone_A(timer):
    socketio.emit('alonetimer', timer, namespace="/alonetimerA")

@socketio.on('alonetimer', namespace="/courtB")
def timer_alone_B(timer):
    socketio.emit('alonetimer', timer, namespace="/alonetimerB")

def new_fixture_slaves(fixture_queue: FixtureQueue, new_fixture, crt):
    fixture_queue.next_fixture()
    socketio.emit('nextfixture', namespace=f"/court{crt}ticker")
    socketio.emit('nextfixture', new_fixture, namespace=f"/court{crt}copy") 
    socketio.emit('nextfixture', namespace=f"/alonetimer{crt}") 
    socketio.emit('nextfixture', namespace=f"/homescore{crt}") 
    socketio.emit('nextfixture', namespace=f"/awayscore{crt}") 
    socketio.emit('nextfixture', namespace=f"/alonetimer{crt}") 
    socketio.emit('nextfixture', namespace=f"/homescore{crt}") 
    socketio.emit('nextfixture', namespace=f"/awayscore{crt}") 

@socketio.on('newfixture', namespace="/courtA")
def new_fixture_ticker_A(new_fixture):
    new_fixture_slaves(fixture_queue_A, new_fixture, "A")

@socketio.on('newfixture', namespace="/courtB")
def new_fixture_ticker_B(new_fixture):
    new_fixture_slaves(fixture_queue_B, new_fixture, "B")

@socketio.on('firstfixture', namespace="/courtA")
def first_fixture_copy_A(current_fixture):
    socketio.emit('firstfixture', current_fixture, namespace="/courtAcopy")

@socketio.on('firstfixture', namespace="/courtB")
def first_fixture_copy_B(current_fixture):
    socketio.emit('firstfixture', current_fixture, namespace="/courtBcopy")

@socketio.on('updateperiod', namespace="/courtA")
def update_period_copy_A(period):
    fixture_queue_A.get_current_fixture().set_current_period(period['sortOrder'])
    socketio.emit('updateperiod', period['displayName'], namespace="/courtAcopy")

@socketio.on('updateperiod', namespace="/courtB")
def update_period_copy_B(period):
    fixture_queue_B.get_current_fixture().set_current_period(period['sortOrder'])
    socketio.emit('updateperiod', period['displayName'], namespace="/courtBcopy")

@socketio.on('playsiren', namespace="/courtA")
def play_siren_copy_A():
    socketio.emit('playsiren', namespace="/courtAcopy")

@socketio.on('playsiren', namespace="/courtB")
def play_siren_copy_B():
    socketio.emit('playsiren', namespace="/courtBcopy")

@socketio.on('showtimeticker', namespace="/courtA")
def show_time_ticker_A():
    socketio.emit('showtimer', namespace="/courtBticker")
    socketio.emit('showtimer', namespace="/alonetimerA")
    socketio.emit('showtimer', namespace="/alonetimerA")

@socketio.on('showtimeticker', namespace="/courtB")
def show_time_ticker_B():
    socketio.emit('showtimer', namespace="/courtBticker")
    socketio.emit('showtimer', namespace="/alonetimerB")

"""
HANDLE GOALS, FOULS AND PENALTY SHOOTOUTS.
"""
def handle_score_update(fixture_queue: FixtureQueue, cursor, crt, update):
    if 'homeGoals' in update:
        fixture_queue.get_current_fixture().set_home_score(update['homeGoals'])
        dbqueue.put((cursor, f"UPDATE fixtures SET home_score = {update['homeGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}ticker")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}copy")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/homescore{crt}")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/homescore{crt}")
    else:
        fixture_queue.get_current_fixture().set_away_score(update['awayGoals'])
        dbqueue.put((cursor, f"UPDATE fixtures SET away_score = {update['awayGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}ticker")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}copy")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/awayscore{crt}")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/awayscore{crt}")

@socketio.on('score', namespace="/courtA")
def score_A(update):
    handle_score_update(fixture_queue_A, cursorA, "A", update)

@socketio.on('score', namespace="/courtB")
def score_B(update):
    handle_score_update(fixture_queue_B, cursorB, "B", update)

def handle_foul_update(fixture_queue: FixtureQueue, crt, update):
    if 'homeFouls' in update:
        fixture_queue.get_current_fixture().set_home_fouls(update['homeFouls'])
        socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/court{crt}copy")
    else:
        fixture_queue.get_current_fixture().set_away_fouls(update['awayFouls'])
        socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/court{crt}copy")

@socketio.on('foul', namespace="/courtA")
def foul_A(update):
    handle_foul_update(fixture_queue_A, "A", update)

@socketio.on('foul', namespace="/courtB")
def foul_B(update):
    handle_foul_update(fixture_queue_B, "B", update)

def handle_went_penalties(fixture_queue: FixtureQueue, crt):
    fixture_queue.get_current_fixture().set_went_penalties(True)
    socketio.emit("wentpenalties", namespace=f"/court{crt}ticker")

@socketio.on('wentpenalties', namespace="/courtA")
def went_penalties_A():
    handle_went_penalties(fixture_queue_A, "A")

@socketio.on('wentpenalties', namespace="/courtB")
def went_penalties_B():
    handle_went_penalties(fixture_queue_B, "B")

def handle_penalty_update(fixture_queue: FixtureQueue, cursor, crt, update):
    if 'homePenalties' in update:
        fixture_queue.get_current_fixture().set_home_penalties(update['homePenalties'])
        dbqueue.put((cursor, f"UPDATE fixtures SET home_penalties = {sum(update['homePenalties'])} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        fixture_queue.get_current_fixture().set_home_penalties_left(update['homePenaltiesLeft'])
        socketio.emit('homepenaltyupdate', update['homePenalties'], namespace=f"/court{crt}ticker")
    else:
        fixture_queue.get_current_fixture().set_away_penalties(update['awayPenalties'])
        dbqueue.put((cursor, f"UPDATE fixtures SET away_penalties = {sum(update['awayPenalties'])} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        fixture_queue.get_current_fixture().set_away_penalties_left(update['awayPenaltiesLeft'])
        socketio.emit('awaypenaltyupdate', update['awayPenalties'], namespace=f"/court{crt}ticker")

@socketio.on('penalty', namespace="/courtA")
def penalty_A(update):
    handle_penalty_update(fixture_queue_A, cursorA, "A", update)

@socketio.on('penalty', namespace="/courtB")
def penalty_B(update):
    handle_penalty_update(fixture_queue_B, cursorB, "B", update)

def handle_sudden_death(fixture_queue: FixtureQueue, crt):
    fixture_queue.get_current_fixture().set_home_penalties_left(1)
    fixture_queue.get_current_fixture().set_away_penalties_left(1)
    socketio.emit('suddendeath', namespace=f"/court{crt}ticker")

@socketio.on('suddendeath', namespace="/courtA")
def sudden_death_A():
    handle_sudden_death(fixture_queue_A, "A")

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
        dbqueue.put((cursor, f"UPDATE fixtures SET home_score = home_score + 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('homegoaladd', namespace=f"/court{crt}ticker")
        socketio.emit('homegoaladd', namespace=f"/court{crt}copy")
    elif update == 'awayGoalIncrement':
        fixture_queue.get_current_fixture().add_away_score(1)
        socketio.emit('awaygoaladd', namespace=f"/court{crt}")
        dbqueue.put((cursor, f"UPDATE fixtures SET away_score = away_score + 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('awaygoaladd', namespace=f"/court{crt}ticker")
        socketio.emit('awaygoaladd', namespace=f"/court{crt}copy")
    elif update == 'homeGoalDecrement':
        fixture_queue.get_current_fixture().add_home_score(-1)
        socketio.emit('homegoaltake', namespace=f"/court{crt}")
        dbqueue.put((cursor, f"UPDATE fixtures SET home_score = home_score - 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('homegoaltake', namespace=f"/court{crt}ticker")
        socketio.emit('homegoaltake', namespace=f"/court{crt}copy")
    elif update == 'awayGoalDecrement':
        fixture_queue.get_current_fixture().add_away_score(-1)
        socketio.emit('awaygoaltake', namespace=f"/court{crt}")
        dbqueue.put((cursor, f"UPDATE fixtures SET away_score = away_score - 1 WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('awaygoaltake', namespace=f"/court{crt}ticker")
        socketio.emit('awaygoaltake', namespace=f"/court{crt}copy")
    elif 'homeGoals' in update:
        fixture_queue.get_current_fixture().set_home_score(update['homeGoals'])
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}")
        dbqueue.put((cursor, f"UPDATE fixtures SET home_score = {update['homeGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}ticker")
        socketio.emit('homescoreupdate', update['homeGoals'], namespace=f"/court{crt}copy")
    elif 'awayGoals' in update:
        fixture_queue.get_current_fixture().set_away_score(update['awayGoals'])
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}")
        dbqueue.put((cursor, f"UPDATE fixtures SET away_score = {update['awayGoals']} WHERE id = {fixture_queue.get_current_fixture().get_id()}"))
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}ticker")
        socketio.emit('awayscoreupdate', update['awayGoals'], namespace=f"/court{crt}copy")

def handle_remote_foul_update(fixture_queue: FixtureQueue, crt, update):
    if update == 'homeFoulIncrement':
        fixture_queue.get_current_fixture().add_home_fouls(1)
        socketio.emit('homefouladd', namespace=f"/court{crt}")
        socketio.emit('homefouladd', namespace=f"/court{crt}copy")
    elif update == 'awayFoulIncrement':
        fixture_queue.get_current_fixture().add_away_fouls(1)
        socketio.emit('awayfouladd', namespace=f"/court{crt}")
        socketio.emit('awayfouladd', namespace=f"/court{crt}copy")
    elif update == 'homeFoulDecrement':
        fixture_queue.get_current_fixture().add_home_fouls(-1)
        socketio.emit('homefoultake', namespace=f"/court{crt}")
        socketio.emit('homefoultake', namespace=f"/court{crt}copy")
    elif update == 'awayFoulDecrement':
        fixture_queue.get_current_fixture().add_away_fouls(-1)
        socketio.emit('awayfoultake', namespace=f"/court{crt}")
        socketio.emit('awayfoultake', namespace=f"/court{crt}copy")
    elif 'homeFouls' in update:
        fixture_queue.get_current_fixture().set_home_fouls(update['homeFouls'])
        socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/court{crt}")
        socketio.emit('homefoulupdate', update['homeFouls'], namespace=f"/court{crt}copy")
    elif 'awayFouls' in update:
        fixture_queue.get_current_fixture().set_away_fouls(update['awayFouls'])
        socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/court{crt}")
        socketio.emit('awayfoulupdate', update['awayFouls'], namespace=f"/court{crt}copy")

@socketio.on('score', namespace="/remoteA")
def remote_score_A(update):
    handle_remote_score_update(fixture_queue_A, cursorA, "A", update)

@socketio.on('score', namespace="/remoteB")
def remote_score_B(update):
    handle_remote_score_update(fixture_queue_B, cursorB, "B", update)

@socketio.on('foul', namespace="/remoteA")
def remote_foul_A(update):
    handle_remote_foul_update(fixture_queue_A, "A", update)

@socketio.on('foul', namespace="/remoteB")
def remote_foul_B(update):
    handle_remote_foul_update(fixture_queue_B, "B", update)

@socketio.on('pause', namespace="/remoteA")
def pause_court_A():
    socketio.emit('pause', namespace="/courtA")

@socketio.on('pause', namespace="/remoteB")
def pause_court_B():
    socketio.emit('pause', namespace="/courtB")

@socketio.on('resume', namespace="/remoteA")
def resume_court_A():
    socketio.emit('resume', namespace="/courtA")

@socketio.on('resume', namespace="/remoteB")
def resume_court_B():
    socketio.emit('resume', namespace="/courtB")

@socketio.on('sirenloop', namespace="/remoteA")
def siren_loop_A():
    socketio.emit('sirenloop', namespace="/courtA")

@socketio.on('sirenloop', namespace="/remoteB")
def siren_loop_B():
    socketio.emit('sirenloop', namespace="/courtB")

@socketio.on('endsirenloop', namespace="/remoteA")
def end_siren_loop_A():
    socketio.emit('endsirenloop', namespace="/courtA")

@socketio.on('endsirenloop', namespace="/remoteB")
def end_siren_loop_B():
    socketio.emit('endsirenloop', namespace="/courtB")

@socketio.on('siren', namespace="/remoteA")
def siren_A():
    socketio.emit('siren', namespace="/courtA")

@socketio.on('siren', namespace="/remoteB")
def siren_B():
    socketio.emit('siren', namespace="/courtB")

@socketio.on('delay', namespace="/remoteA")
def delay_court_A(time):
    fixture_queue_A.move_fixture_times(time)
    socketio.emit('delay', time,  namespace="/courtA")

@socketio.on('delay', namespace="/remoteB")
def delay_court_B(time):
    fixture_queue_B.move_fixture_times(time)
    socketio.emit('delay', time, namespace="/courtB")

@socketio.on('bringforward', namespace="/remoteA")
def bring_forward_court_A(time):
    fixture_queue_A.move_fixture_times(-time)
    socketio.emit('bringforward', time,  namespace="/courtA")

@socketio.on('bringforward', namespace="/remoteB")
def bring_forward_court_B(time):
    fixture_queue_B.move_fixture_times(-time)
    socketio.emit('bringforward', time, namespace="/courtB")

@socketio.on('startperiod', namespace="/remoteA")
def start_period_A():
    socketio.emit('startperiod', namespace="/courtA")

@socketio.on('startperiod', namespace="/remoteB")
def start_period_B():
    socketio.emit('startperiod', namespace="/courtB")

@socketio.on('startnextgame', namespace="/remoteA")
def start_game_A():
    socketio.emit('startnextgame', namespace="/courtA")

@socketio.on('startnextgame', namespace="/remoteB")
def start_game_B():
    socketio.emit('startnextgame', namespace="/courtB")

@socketio.on('disconnect')
def disconnect():
    pass

if __name__ == '__main__' and (fixture_queue_A.has_games() or fixture_queue_B.has_games()):
    if not fixture_queue_A.has_games():
        courtAfinished = True
    elif not fixture_queue_B.has_games():
        courtBfinished = True
    if db_thread is None:
        db_thread = Thread(target=dbconsumer)
        db_thread.daemon = True
        db_thread.start()
    socketio.run(app, host="0.0.0.0", port=80)
else:
    cursorA.close()
    cursorB.close()
    db.close()