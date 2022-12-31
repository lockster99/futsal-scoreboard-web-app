from selenium import webdriver
import selenium
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable

from model.db import db_connection
#from db import db_connection
#from entities import Competition, Team, Fixture, FixtureQueue
from model.entities import Competition, PeriodConfiguration, Period, Team, Fixture, FixtureQueue
from webdriver_manager.firefox import GeckoDriverManager

import imaplib
import email
import os
import time
from datetime import datetime, timedelta
from sys import platform

from imap_tools import MailBox, AND

import csv

DIRPI = "/home/pi/Desktop/Scoreboard_javascript"

def setup_webdriver():
    fp = webdriver.FirefoxProfile()
    op = webdriver.FirefoxOptions()
    op.set_headless()
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", DIRPI)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
    if platform == "linux" or platform == "linux2":
        return webdriver.Firefox(firefox_profile=fp, options=op, executable_path="/usr/local/bin/geckodriver")
    elif platform == "darwin":
        pass
    elif platform == "win32":
        return webdriver.Firefox(firefox_profile=fp, options=op, executable_path="C:/Users/lachi/Downloads/geckodriver-v0.30.0-win64/geckodriver.exe")
    

    #return webdriver.Firefox(firefox_profile=fp, executable_path="/usr/local/bin/geckodriver")

def login_sportstg(driver):
    driver.get("https://passport.mygameday.app//login/")
    driver.find_element_by_id("login-email").find_element_by_class_name("required").send_keys("lachieblaine@hotmail.com")
    driver.find_element_by_id("login-password").find_element_by_class_name("required").send_keys("G7nk9tAL1@35")
    driver.find_element_by_class_name("button--primary").click()

def logout_sportstg(driver):
    driver.get("https://passport.mygameday.app//logout/?")

def sportstg_publish_to_web(driver):
    driver.get("https://passport.mygameday.app/account/?")
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.CLASS_NAME, "mod-option-link"))).click()
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.CLASS_NAME, "org-list-entry"))).click()
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.XPATH, "//div[@id='menu_wrap']/ul/li[3]/a"))).click()
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.XPATH, "//div[@id='menu_wrap']/ul/li[3]/ul/li[3]/a"))).click()
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.ID, "btnUpload"))).click()
    WebDriverWait(driver, 20).until(ec.alert_is_present())
    driver.switch_to.alert.accept()

def insert_results_sportstg(driver, cursor):
    driver.get("https://membership.mygameday.app/authlist.cgi?results=1")
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.CLASS_NAME, "org-list-entry"))).click()
    today_date = datetime.now().date()
    dtFrom = driver.find_element_by_name('dtFrom')
    dtTo = driver.find_element_by_name('dtTo')
    dtFrom.send_keys(Keys.CONTROL, 'a')
    dtFrom.send_keys(Keys.BACKSPACE)
    dtFrom.send_keys(today_date.strftime("%d/%m/%Y"))
    dtTo.send_keys(Keys.CONTROL, 'a')
    dtTo.send_keys(Keys.BACKSPACE)
    dtTo.send_keys(today_date.strftime("%d/%m/%Y"))
    dtTo.send_keys(Keys.ENTER)
    dtTo.send_keys(Keys.ENTER)
    time.sleep(5)
    WebDriverWait(driver, 15).until(element_to_be_clickable((By.NAME, "submit_qr"))).click()
    cursor.execute("""SELECT f.home_score, f.home_penalties, f.away_score, f.away_penalties, f.match_datetime, f.venue FROM fixtures AS f, competitions AS c
    WHERE f.competition=c.id 
    AND c.auto_upload_results = 1
    AND f.match_date=CURRENT_DATE 
    ORDER BY f.match_datetime ASC, f.venue ASC""")
    for i, result in enumerate(cursor.fetchall()):
        # if result[2].strftime('%d/%m/%Y %H:%M') == driver.find_element_by_xpath(f"//table[@id='DataTables_Table_0']/tbody/tr[{i+1}]/td[8]").text and \
        #         result[3] == driver.find_element_by_xpath(f"//table[@id='DataTables_Table_0']/tbody/tr[{i+1}]/td[9]").text:
        driver.find_element_by_xpath(f"//table[@id='DataTables_Table_0']/tbody/tr[{i+1}]/td[1]/div/label/input").send_keys(result[0]+result[1])
        driver.find_element_by_xpath(f"//table[@id='DataTables_Table_0']/tbody/tr[{i+1}]/td[5]/div/label/input").send_keys(result[2]+result[3])
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.CLASS_NAME, 'quick-save'))).click()
    #WebDriverWait(driver, 20).until(element_to_be_clickable((By.XPATH, "//div[@id='match-list-nav']/input[1]"))).click()

def email_csv(driver):
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.CLASS_NAME, "mod-option-link"))).click()
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.CLASS_NAME, "org-list-entry"))).click()
    WebDriverWait(driver, 20).until(element_to_be_clickable((By.XPATH, "//div[@id='menu_wrap']/ul/li[8]/a"))).click()
    try:
        WebDriverWait(driver, 8).until(element_to_be_clickable((By.ID, "wizclosebtn"))).click()
    except TimeoutException:
        pass
    pageholder = driver.find_element_by_id("pageholder")
    driver.execute_script("window.scrollTo(arguments[0].scrollWidth, arguments[0].scrollHeight);", pageholder)
    Select(driver.find_element_by_id("prerep_ID16")).select_by_value('573658')
    driver.find_elements_by_class_name("ROButRun")[2].click()

def download_report():
    mailb = MailBox('outlook.office365.com').login('lachieblaine@hotmail.com', 'helenst2014', 'Sportstg Reports')
    date_utc = (datetime.now()-timedelta(hours=10)).date()
    latest_report = next(mailb.fetch(AND(date=date_utc))).attachments[0]
    if platform == "linux" or platform == "linux2":
        with open(f"{DIRPI}/{latest_report.filename}", 'wb') as f:
            f.write(latest_report.payload)
    elif platform == "win32":
        with open(f"{os.getcwd()}\\{latest_report.filename}", 'wb') as f:
            f.write(latest_report.payload)

def get_current_season(cursor):
    cursor.execute("SELECT CURRENT_SEASON() AS CURRENT_SEASON")
    return cursor.fetchone()[0]

def get_competitions(cursor, season: str):
    cursor.execute(f"""SELECT sc.competition_id, sc.season_id, c.name, c.auto_upload_results, c.show_score, c.show_teams FROM season_competitions as sc 
                        INNER JOIN competitions AS c ON sc.competition_id = c.id 
                        AND sc.season_id = '{season}'""")
    return {row[0]: Competition(row[0], row[1], row[2], bool(row[3]), bool(row[4]), bool(row[5])) for row in cursor.fetchall()}

def get_teams(cursor, season: str, competitions: dict):
    cursor.execute(f"""SELECT t.id, ct.competition_id, t.name, t.colour, t.abbreviation, t.logo FROM competition_teams AS ct 
                        INNER JOIN teams AS t ON ct.team_id = t.id AND ct.season_id = '{season}' 
                        AND ct.competition_id IN {create_string_tuple(competitions.keys())}""")
    return [Team(row[0], row[1], row[2], row[3], row[4], row[5]) for row in cursor.fetchall()]

def upload_new_fixtures(cursor):
    current_season_id = get_current_season(cursor)
    competitions = get_competitions(cursor, current_season_id)
    teams = get_teams(cursor, current_season_id, competitions)
    cursor.execute(f"DELETE FROM fixtures WHERE match_date >= CURRENT_DATE")
    with open("reportdata.csv", 'r') as fixturefile:
        reader = csv.DictReader(fixturefile)
        for row in reader:
            if row.get("Season") != "" and row.get("Match Date") != "":
                match_date = datetime.strptime(row.get("Match Date"), "%d/%m/%Y")
                if row.get("Venue Name") != "" and match_date.date() >= datetime.now().date():
                    comp_id = get_competition_id(competitions.values(), current_season_id, row.get("Competition Name"))
                    home_id = get_team_id(teams, comp_id, row.get("Team 1"))
                    # TODO: Add team if it doesn't exist in database
                    # if home_id == None:
                    away_id = get_team_id(teams, comp_id, row.get("Team 2"))
                    # TODO: Add team if it doesn't exist in database
                    # if away_id == None:
                    match_datetime_str = str(datetime.strptime(f"{str(match_date.date())} {row.get('Match Time')}", "%Y-%m-%d %I:%M:%S %p"))
                    if home_id != None and away_id != None:
                        print(f'Inserted fixture {(row.get("Match ID"), row.get("Season"), comp_id, row.get("Round Type"), row.get("Round Number"), home_id, 0, 0, away_id, str(match_date), match_datetime_str, row.get("Venue Name"), 0, 0)}')
                        cursor.execute("INSERT INTO fixtures VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                (row.get("Match ID"), row.get("Season"), comp_id, row.get("Round Type"), 
                                row.get("Round Number"), home_id, 0, 0, away_id, str(match_date),
                                match_datetime_str, row.get("Venue Name"), 0, 0))

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

def get_period_configuration(cursor, competiton_id, round_type):
    cursor.execute(f"""SELECT cpc.period_config_id, pc.name, pc.round_type, pc.minimum_pregame, pc.description FROM competition_period_configurations AS cpc 
                        INNER JOIN period_configurations AS pc ON pc.id = cpc.period_config_id 
                        AND cpc.competition_id = {competiton_id} 
                        AND pc.round_type = '{round_type}'""")
    row = cursor.fetchone()
    return PeriodConfiguration(row[0], row[1], row[2], row[3], row[4], get_periods(cursor, row[0]))

def get_today_fixtures_db(cursor, venue):
    fixtures = []
    current_season_id = get_current_season(cursor)
    competitions = get_competitions(cursor, current_season_id)
    teams = {team.get_id(): team for team in get_teams(cursor, current_season_id, competitions)}
    cursor.execute(f"SELECT * FROM fixtures WHERE match_date = CURRENT_DATE AND match_datetime >= CURRENT_TIMESTAMP AND venue = '{venue}' ORDER BY match_datetime ASC")
    for row in cursor.fetchall():
        period_configuration = get_period_configuration(cursor, row[2], row[3])
        fixtures.append(Fixture(row[0], competitions[row[2]], row[3], row[4], teams[row[5]], row[6], row[7], teams[row[8]], row[10], row[11], row[12], row[13], period_configuration))
    return FixtureQueue(fixtures)

def upload_scores_sportstg():
    driver = setup_webdriver()
    login_sportstg(driver)