#from model.db import db_connection
#from db import db_connection
#from entities import Competition, Team, Fixture, FixtureQueue
from model.entities import Competition, PeriodConfiguration, Period, Team, Fixture, FixtureQueue

import os
import time
from datetime import datetime, timedelta
from sys import platform

import csv

DIRPI = "/home/pi/Desktop/Scoreboard_javascript"

def get_current_season(cursor):
    cursor.execute("SELECT id FROM seasons WHERE date('now') BETWEEN start_date AND end_date")
    season = cursor.fetchone()[0]
    return season
    cursor.execute("SELECT id FROM seasons WHERE date('now') BETWEEN start_date AND end_date")
    season = cursor.fetchone()[0]
    return season

def get_competitions(cursor, season: str):
    cursor.execute(f"""SELECT sc.competition_id, sc.season_id, c.name, c.auto_upload_results, c.show_score, c.show_teams, c.regular_period_configuration, c.finals_period_configuration 
                        FROM season_competitions as sc""")
    cursor.execute(f"""SELECT sc.competition_id, sc.season_id, c.name, c.auto_upload_results, c.show_score, c.show_teams, c.regular_period_configuration, c.finals_period_configuration 
                        FROM season_competitions as sc 
                        INNER JOIN competitions AS c ON sc.competition_id = c.id 
                        AND sc.season_id = '{season}'""")
    return {row[0]: Competition(row[0], row[1], row[2], bool(row[3]), bool(row[4]), bool(row[5])) for row in cursor.fetchall()}

def get_teams(cursor, season: str, competitions: dict):
    cursor.execute(f"""SELECT t.id, ct.competition_id, t.name, t.colour, t.abbreviation, t.logo FROM competition_teams AS ct 
                        INNER JOIN teams AS t ON ct.team_id = t.id AND ct.season_id = '{season}' 
                        AND ct.competition_id IN {create_string_tuple(competitions.keys())}""")
    return [Team(row[0], row[1], row[2], row[3], row[4], row[5]) for row in cursor.fetchall()]

def parse_home_score(score_str):
    try:
        return int(score_str)
    except:
        return 0

def create_string_tuple(iterable, empty: bool = True):
    if len(iterable) == 0:
        if empty:
            return "()"
        raise ValueError
    if len(iterable) == 1:
        listiter = list(iterable)
        return f"({listiter[0]})"
    return str(tuple(iterable))
    
def get_competition_id(competitions, season, competition_name):
    for comp in competitions:
        if str(comp.get_season()) == season and comp.get_name() == competition_name:
            return comp.get_id()
    return None

def get_team_id(teams, comp_id, name):
    for team in teams:
        if team.get_competition_id() == comp_id and team.get_name() == name:
            return team.get_id()
    return None

def get_periods(cursor, configuration_id):
    cursor.execute(f"""SELECT * FROM period_config_periods AS pcp
                        INNER JOIN periods AS p ON pcp.period_id = p.id
                        AND pcp.configuration_id = {configuration_id}
                        ORDER BY sort_order ASC""")
    return [Period(row[3], row[4], row[5], row[6], row[7], bool(row[8]), bool(row[9]), bool(row[10]), 
                    bool(row[11]), bool(row[12]), bool(row[13]), bool(row[14]), bool(row[15]), bool(row[16]), 
                    bool(row[17]), bool(row[18]), row[2]) for row in cursor.fetchall()]

def get_period_configuration(cursor, competition_id, round_type):
    period_config_id = 1
    if round_type == "Regular":
        cursor.execute(f"""SELECT regular_period_configuration FROM competitions
                            WHERE id = {competition_id}""")
        period_config_id = cursor.fetchone()[0]
    elif round_type == "Finals":
        cursor.execute(f"""SELECT finals_period_configuration FROM competitions
                            WHERE id = {competition_id}""")
        period_config_id = cursor.fetchone()[0]

    cursor.execute(f"SELECT * FROM period_configurations WHERE id = {period_config_id}")
def get_period_configuration(cursor, competition_id, round_type):
    period_config_id = 1
    if round_type == "Regular":
        cursor.execute(f"""SELECT regular_period_configuration FROM competitions
                            WHERE id = {competition_id}""")
        period_config_id = cursor.fetchone()[0]
    elif round_type == "Finals":
        cursor.execute(f"""SELECT finals_period_configuration FROM competitions
                            WHERE id = {competition_id}""")
        period_config_id = cursor.fetchone()[0]

    cursor.execute(f"SELECT * FROM period_configurations WHERE id = {period_config_id}")
    row = cursor.fetchone()
    return PeriodConfiguration(row[0], row[1], row[2], row[3], row[4], get_periods(cursor, row[0]))

def get_today_fixtures_db(cursor, venue):
    fixtures = []
    current_season_id = get_current_season(cursor)
    competitions = get_competitions(cursor, current_season_id)
    teams = {team.get_id(): team for team in get_teams(cursor, current_season_id, competitions)}
    cursor.execute(f"SELECT * FROM fixtures WHERE match_datetime >= CURRENT_TIMESTAMP AND venue = '{venue}' ORDER BY match_datetime ASC")
    for row in cursor.fetchall():
        period_configuration = get_period_configuration(cursor, row[2], row[3])
        fixtures.append(Fixture(row[0], competitions[row[2]], row[3], row[4], teams[row[5]], row[6], row[7], teams[row[8]], datetime.strptime(row[9],"%Y-%m-%d %H:%M:%S"), row[10], row[11], row[12], period_configuration))
    return FixtureQueue(fixtures)