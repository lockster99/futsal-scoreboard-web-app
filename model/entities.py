from datetime import datetime, date, timedelta
from model.functions import fetch_fixtures_json, filter_fixtures_json_by_court, get_team_logos_from_squadi, download_image

second = 1000
minute = 60*second

units_divide = {'mus': 1/1000, 'ms': 1, 's': 1000, 'm': 60000, 'h': 360000, 'd': 360000*24}

class NameObject(object):
    """
    A general abstract class for objects that have an id and name attribute.
    """
    def __init__(self, id: int, name: str):
        self._id = id
        self._name = name

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name


class Season(NameObject):
    """
    A class (which inherits NameObject) to represent a season
    """
    def __init__(self, id: int, name: str):
        super().__init__(id, name)


class PeriodConfiguration(NameObject):
    """
    A class that contains a list of ordered periods and their configuration
    """
    def __init__(self, id: int, name: str, round_type: str, minimum_pregame: int, description: str, periods: list):
        super().__init__(id, name)
        self._round_type = round_type
        self._minimum_pregame = minimum_pregame
        self._description = description
        self._periods = periods

    def get_json(self):
        return {
            'id': self._id,
            'name': self._name,
            'roundType': self._round_type,
            'minimumPregame': self._minimum_pregame,
            'description': self._description,
            'periods': [period.get_json() for period in self._periods]
        }

    def get_round_type(self):
        return self._round_type

    def set_round_type(self, round_type: str):
        self._round_type = round_type

    def get_description(self):
        return self._description

    def set_description(self, description: str):
        self._description = description

    def get_periods(self):
        return self._periods

    def set_periods(self, periods: list):
        self._periods = periods

    def period_sort_order(self, period):
        return period.get_sort_order()

    def resort_periods(self):
        self._periods.sort(key=self.period_sort_order)

class Period(NameObject):
    """
    A class which contains a period and relevant information and configurations.
    """
    def __init__(self, id: int, name: str, display_name: str, length: int, description: str, auto_start: bool, can_pause: bool, count_up: bool, end_siren: bool, last_minute_decimal: bool, reset_fouls: bool, show_time: bool, show_time_zero: bool, show_time_ticker: bool, decides_extra_time: bool, decides_penalties: bool, sort_order: int):
        super().__init__(id, name)
        self._display_name = display_name
        self._length = length #in milliseconds
        self._description = description
        self._auto_start = auto_start
        self._can_pause = can_pause
        self._count_up = count_up
        self._end_siren = end_siren
        self._last_minute_decimal = last_minute_decimal
        self._reset_fouls = reset_fouls
        self._show_time = show_time
        self._show_time_zero = show_time_zero
        self._show_time_ticker = show_time_ticker
        self._decides_extra_time = decides_extra_time
        self._decides_penalties = decides_penalties
        self._sort_order = sort_order

    def get_json(self):
        return {
            'id': self._id,
            'fullName': self._name,
            'displayName': self._display_name,
            'periodLength': self._length,
            'autoStart': self._auto_start,
            'canPause': self._can_pause,
            'countUp': self._count_up,
            'endSiren': self._end_siren,
            'lastMinuteDecimal': self._last_minute_decimal,
            'resetFouls': self._reset_fouls,
            'showTime': self._show_time,
            'showTimeZero': self._show_time_zero,
            'showTimeTicker': self._show_time_ticker,
            'decidesExtraTime': self._decides_extra_time,
            'decidesPenalties': self._decides_penalties,
            'sortOrder': self._sort_order
        }

    def get_length(self):
        return self._length
    
    def get_length_in(self, unit: str):
        if unit in units_divide:
            if self._length == None:
                return 0
            return self._length/units_divide[unit]
        raise ValueError("Invalid unit.")

    def set_length(self, length: int):
        self._length = length

    def set_length_in(self, length: int, unit: str):
        if unit in units_divide:
            self._length = length*units_divide[str]
        raise ValueError("Invalid unit.")

    def get_display_name(self):
        return self._display_name

    def set_display_name(self, display_name):
        self._display_name = display_name

    def auto_start(self):
        return self._auto_start

    def set_auto_start(self, auto_start: bool):
        self._auto_start = auto_start

    def can_pause(self):
        return self._can_pause

    def set_can_pause(self, can_pause: bool):
        self._can_pause = can_pause

    def count_up(self):
        return self._count_up

    def set_count_up(self, count_up: bool):
        self._count_up = count_up

    def end_siren(self):
        return self._end_siren

    def set_end_siren(self, end_siren: bool):
        self._end_siren = end_siren

    def last_minute_decimal(self):
        return self._last_minute_decimal

    def set_last_minute_decimal(self, last_minute_decimal: bool):
        self._last_minute_decimal = last_minute_decimal

    def reset_fouls(self):
        return self._last_minute_decimal

    def set_reset_fouls(self, reset_fouls: bool):
        self._reset_fouls = reset_fouls
    
    def show_time_zero(self):
        return self._show_time_zero

    def set_show_time_zero(self, show_time_zero: bool):
        self._show_time_zero = show_time_zero

    def show_time_ticker(self):
        return self._show_time_ticker

    def set_show_time_ticker(self, show_time_ticker: bool):
        self._show_time_ticker = show_time_ticker

    def decides_extra_time(self):
        return self._decides_extra_time

    def set_decides_extra_time(self, decides_extra_time: bool):
        self._decides_extra_time = decides_extra_time

    def decides_penalties(self):
        return self._decides_penalties

    def set_decides_penalties(self, decides_penalties: bool):
        self._decides_penalties = decides_penalties

    def get_sort_order(self):
        return self._sort_order

    def set_sort_order(self, sort_order):
        self._sort_order = sort_order


class Competition(NameObject):
    """
    A class to represent a competition
    """
    def __init__(self, id: int, season: str, name: str, auto_upload_results: bool, show_score: bool, show_teams: bool):
        super().__init__(id, name)
        self._season = season
        self._auto_upload_results = auto_upload_results
        self.show_score = show_score 
        self.show_teams = show_teams

    def get_season(self):
        return self._season
        
    def get_full_name(self):
        return f"{self._name} {self._season}"

    def get_auto_upload_results(self):
        return self._auto_upload_results


class Team(NameObject):
    """
    A class (which inherits NameObject) to represent a team
    """
    def __init__(self, id: int, competition_id: int, name: str, colour: str, abbreviation: str, logo: str):
        super().__init__(id, name)
        self._competition_id = competition_id
        self._colour = colour
        self._abbreviation = abbreviation
        self._logo = logo

    def get_competition_id(self):
        return self._competition_id
        
    def get_colour(self):
        return self._colour
    
    def set_colour(self, colour):
        self._colour = colour

    def get_abbreviation(self):
        return self._abbreviation
    
    def set_abbreviation(self, abbreviation):
        self._abbreviation = abbreviation

    def get_logo(self):
        return self._logo
    
    def set_logo(self, logo):
        self._logo = logo


class Fixture(object):
    """
    A class which represents a general fixture
    """
    def __init__(self, id: int, competition: Competition, round_type: str, round: int,
                home_team: Team, home_score: int, away_score: int, away_team: Team,
                datetime: datetime, venue: str, home_penalties: int, away_penalties: int, period_configuration: PeriodConfiguration):
        self._id = id
        self._competition = competition
        self._round_type = round_type
        self._round = round
        self._home_team = home_team
        self._home_score = home_score
        self._home_fouls = 0
        self._away_fouls = 0
        self._away_score = away_score
        self._went_penalties = False
        self._home_penalties = []
        self._away_penalties = []
        self._home_penalties_left = 5
        self._away_penalties_left = 5
        self._home_number_penalties = home_penalties
        self._away_number_penalties = away_penalties
        self._away_team = away_team
        self._datetime = datetime
        self._venue = venue
        self._period_configuration = period_configuration
        self._current_period = 0

    def get_id(self):
        return self._id

    def get_competition(self):
        return self._competition

    def get_round_type(self):
        return self._round_type
    
    def get_round(self):
        return self._round

    def get_home_team(self):
        return self._home_team

    def get_home_score(self):
        return self._home_score

    def set_home_score(self, home_score):
        self._home_score = home_score

    def get_away_score(self):
        return self._away_score

    def set_away_score(self, away_score):
        self._away_score = away_score

    def get_home_fouls(self):
        return self._home_fouls

    def set_home_fouls(self, fouls):
        self._home_fouls = fouls

    def get_away_fouls(self):
        return self._away_fouls

    def set_away_fouls(self, fouls):
        self._away_fouls = fouls

    def get_went_penalties(self):
        return self._went_penalties

    def set_went_penalties(self, went_penalties):
        self._went_penalties = went_penalties

    def get_home_penalties(self):
        return self._home_penalties

    def set_home_penalties(self, penalties):
        self._home_penalties = penalties

    def get_away_penalties(self):
        return self._away_penalties

    def set_away_penalties(self, penalties):
        self._away_penalties = penalties

    def get_home_penalties_left(self):
        return self._home_penalties_left

    def set_home_penalties_left(self, num_left):
        self._home_penalties_left = num_left

    def get_away_penalties_left(self):
        return self._away_penalties_left

    def set_away_penalties_left(self, num_left):
        self._away_penalties_left = num_left

    def get_home_number_penalties(self):
        return sum(self._home_penalties)
    
    def get_away_number_penalties(self):
        return sum(self._away_penalties)

    def get_away_team(self):
        return self._away_team

    def get_datetime(self):
        return self._datetime

    def get_date(self):
        return self._datetime.date

    def get_time(self):
        return self._datetime.time

    def get_venue(self):
        return self._venue 

    def get_period_configuration(self):
        return self._period_configuration

    def get_current_period(self):
        return self._period_configuration.get_periods()[self._current_period]

    def set_current_period(self, current_period: int):
        self._current_period = current_period

    def get_penalties_scored(pen_list):
        scored = 0
        for pen in pen_list:
            if pen == 1:
                scored += 1
        return scored

    def get_home_penalties_scored(self):
        return self.get_penalties_scored(self._home_penalties)

    def get_away_penalties_scored(self):
        return self.get_penalties_scored(self._away_penalties)

    def add_home_score(self, score):
        if (self._home_score + score) >= 0: 
            self._home_score += score

    def add_away_score(self, score):
        if (self._away_score + score) >= 0:
            self._away_score += score

    def add_home_fouls(self, fouls):
        if (self._home_fouls + fouls) >= 0:
            self._home_fouls += fouls

    def add_away_fouls(self, fouls):
        if (self._away_fouls + fouls) >= 0:
            self._away_fouls += fouls
    
    def get_json(self):
        return {"id": self._id,
                "season": self._competition.get_season(),
                "competition": self._competition.get_name(),
                "showScore": self._competition.show_score,
                "showTeams": self._competition.show_teams,
                "roundType": self._round_type,
                "round": self._round,
                "court": f"Court {self._venue[-1]}",
                "homeId": self._home_team.get_id(),
                "awayId": self._away_team.get_id(),
                "homeColour": self._home_team.get_colour(),
                "awayColour": self._away_team.get_colour(),
                "homeName": self._home_team.get_name(),
                "awayName": self._away_team.get_name(),
                "homeAbbrev": self._home_team.get_abbreviation(),
                "awayAbbrev": self._away_team.get_abbreviation(),
                "homeGoals": self._home_score,
                "awayGoals": self._away_score,
                "homeFouls": self._home_fouls,
                "awayFouls": self._away_fouls,
                "wentPenalties": self._went_penalties,
                "homePenalties": self._home_penalties,
                "awayPenalties": self._away_penalties,
                "homePenaltiesLeft": self._home_penalties_left,
                "awayPenaltiesLeft": self._away_penalties_left,
                "gameTime": str(self._datetime),
                "periodConfiguration": self._period_configuration.get_json(),
                "currentPeriod": self._current_period,
                "venue": self._venue,
                "homeLogo": self._home_team.get_logo(),
                "awayLogo": self._away_team.get_logo()
        }
    
    def move_game_time(self, delta):
        print(type(self._datetime), self._datetime)
        print(type(delta), delta)
        self._datetime += timedelta(milliseconds=delta)


class FixtureQueue(object):
    """
    The class that contains and manages a queue of fixtures.
    """
    def __init__(self, fixtures: list):
        self._fixtures = fixtures
        self._current = 0
        self._ticker_connected = False
        self._copy_connected = False
        self._alonetimer_connected = False

    def get_fixtures(self):
        return self._fixtures

    def get_current_fixture(self):
        return self._fixtures[self._current]

    def next_fixture(self):
        if self._current < len(self._fixtures)-1:
            self._current += 1
            return True
        return False

    def previous_fixture(self):
        if self._current > 0:
            self._current -= 1
            return True
        return False

    def remaining_fixtures(self):
        return self._fixtures[self._current:]

    def has_games(self):
        if len(self._fixtures) <= self._current:
            return False
        return True

    def get_json(self):
        fixture_list = [fixture.get_json() for fixture in self.remaining_fixtures()]
        return {"fixtures": fixture_list, "current": self._current, "firstGameTime": str(self._fixtures[0].get_datetime())}

    def move_fixture_times(self, delta):
        for fixture in self._fixtures[self._current:]:
            fixture.move_game_time(delta)

    def need_upload_results(self):
        for fixture in self._fixtures:
            if fixture.get_competition().get_auto_upload_results():
                return True
        return False

    def ticker_connected(self):
        return self._ticker_connected

    def copy_connected(self):
        return self._copy_connected
    
    def alonetimer_connected(self):
        return self._alonetimer_connected

    def set_ticker_connected(self, connected: bool):
        self._ticker_connected = connected

    def set_copy_connected(self, connected: bool):
        self._copy_connected = connected

    def set_alonetimer_connected(self, connected: bool):
        self._alonetimer_connected = connected




COMMUNITY_PRE_GAME = Period(0, "Pre game", "Pre game", None, "", True, False, False, False, False, True, True, False, False, False, False, 0)
COMMUNITY_FIRST_HALF = Period(1, "First half", "First half", 13*minute, "", True, False, False, True, True, True, True, False, True, False, False, 1)
COMMUNITY_HALF_TIME = Period(2, "Half time", "Half time", 2*minute, "", True, False, False, False, False, False, True, False, False, False, False, 2)
COMMUNITY_SECOND_HALF = Period(3, "Second half", "Second half", 13*minute, "", True, False, False, True, True, True, True, False, True, False, False, 3)
COMMUNITY_FULL_TIME = Period(4, "Full time", "Full time", 15*second, "", True, False, False, False, False, False, False, False, False, False, False, 4)
COMMUNITY_PERIODS = [COMMUNITY_PRE_GAME, COMMUNITY_FIRST_HALF, COMMUNITY_HALF_TIME, COMMUNITY_SECOND_HALF, COMMUNITY_FULL_TIME]
COMMUNITY_PERIOD_CONFIGURATION = PeriodConfiguration(2, "Community Standard", "Normal", 1*minute, "Standard Community period configuration", COMMUNITY_PERIODS)


F_LEAGUE_PRE_GAME = Period(0, "Pre game", "Pre game", None, "", True, True, False, False, False, True, True, False, False, False, False, 0)
F_LEAGUE_FIRST_HALF = Period(1, "First half", "First half", 20*minute, "", False, True, False, True, True, True, True, False, True, False, False, 1)
F_LEAGUE_HALF_TIME = Period(2, "Half time", "Half time", 8*minute, "", True, True, False, False, False, False, False, False, False, False, False, 2)
F_LEAGUE_SECOND_HALF = Period(3, "Second half", "Second half", 20*minute, "", False, True, False, True, True, True, True, False, True, False, False, 3)
F_LEAGUE_FULL_TIME = Period(4, "Full time", "Full time", 5*minute, "", True, True, False, False, False, False, False, False, False, False, False, 4)
F_LEAGUE_PERIODS = [F_LEAGUE_PRE_GAME, F_LEAGUE_FIRST_HALF, F_LEAGUE_HALF_TIME, F_LEAGUE_SECOND_HALF, F_LEAGUE_FULL_TIME]
F_LEAGUE_PERIOD_CONFIGURATION = PeriodConfiguration(1, "F-League Standard", "Normal", 1*minute, "Standard F-League period configuration", F_LEAGUE_PERIODS)


def get_logo_name(team_name: str, team_logos: set):
    if team_name in team_logos:
        return f"{team_name}-logo"
    return "ipswich-futsal-rgb"

def fix_fleague_team_name(team_name: str):
    team_names = {
        "Ipswich Futsal Club": "Ipswich Futsal",
        "Brisbane EliteFoot Futsal Club": "EliteFoot FC",
        "Sala Time Futsal Club": "Sala Time",
        "South Brisbane Fury Futsal Club": "SB Fury",
        "Crusaders Futsal Club": "Crusaders FC",
        "River City Futsal Club": "River City",
        "Sunshine Coast Wave Futsal Club": "SC Wave",
        "Gold Coast Galaxy Futsal Club": "GC Galaxy"}
    if team_name in team_names:
        return team_names[team_name]
    return team_name

def load_default_fixture_queue(court_number: int):
    try:
        squadi_fixtures_json = filter_fixtures_json_by_court(fetch_fixtures_json(), court_number=court_number)
        community_logos = get_team_logos_from_squadi()
        team_logos = community_logos | get_team_logos_from_squadi(competition_id=1096)
        fixture_queue_list = list()
        for fixture in squadi_fixtures_json['matches']:
            home_team = Team(fixture['team1']['id'], 1, fix_fleague_team_name(fixture['team1']['name']), "green", f"{fixture['team1']['name'][:3]}".upper(), get_logo_name(fixture['team1']['name'], team_logos))
            away_team = Team(fixture['team2']['id'], 1, fix_fleague_team_name(fixture['team2']['name']), "white", f"{fixture['team2']['name'][:3]}".upper(), get_logo_name(fixture['team2']['name'], team_logos))
            competition = Competition(fixture['competition']['id'], "2025", fixture['competition']['name'], False, True, True)
            period_configuration = COMMUNITY_PERIOD_CONFIGURATION
            if competition.get_name() == "F-League 2025":
                period_configuration = F_LEAGUE_PERIOD_CONFIGURATION
            fixture_obj = Fixture(fixture['id'], competition, "Normal round", fixture['round'], home_team, 0, 0, away_team,
                                datetime.fromisoformat(fixture['startTime'].replace("Z", "+00:00")), "Court B", 0, 0, period_configuration)
            fixture_queue_list.append(fixture_obj)
        # sort fixture queue list by match start time
        fixture_queue_list.sort(key=lambda x: x.get_datetime())
        fixture_queue = FixtureQueue(fixture_queue_list)
        return fixture_queue
    except Exception as e:
        pre_game = Period(
            id=0, 
            name="Pre game", 
            display_name="Pre game", 
            length=None, 
            description="", 
            auto_start=True, 
            can_pause=True, 
            count_up=False, 
            end_siren=False, 
            last_minute_decimal=False, 
            reset_fouls=True, 
            show_time=True, 
            show_time_zero=False, 
            show_time_ticker=False, 
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=0
        )
        first_half = Period(
            id=1, 
            name="First half", 
            display_name="First half", 
            length=20*minute, 
            description="", 
            auto_start=False, 
            can_pause=True, 
            count_up=False, 
            end_siren=True, 
            last_minute_decimal=True, 
            reset_fouls=True, 
            show_time=True, 
            show_time_zero=False, 
            show_time_ticker=True, 
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=1
        )
        half_time = Period(
            id=2, 
            name="Half time", 
            display_name="Half time", 
            length=1*minute, 
            description="", 
            auto_start=True, 
            can_pause=True, 
            count_up=False, 
            end_siren=False, 
            last_minute_decimal=False, 
            reset_fouls=False, 
            show_time=False, 
            show_time_zero=True, 
            show_time_ticker=False, 
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=2
        )
        second_half = Period(
            id=3, 
            name="Second half", 
            display_name="Second half", 
            length=20*minute, 
            description="", 
            auto_start=False, 
            can_pause=True, 
            count_up=False, 
            end_siren=True, 
            last_minute_decimal=True, 
            reset_fouls=True, 
            show_time=True, 
            show_time_zero=False,
            show_time_ticker=True,
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=3
        )
        normal_full_time = Period(
            id=4, 
            name="Normal full time", 
            display_name="Normal full time", 
            length=15*second, 
            description="",
            auto_start=True, 
            can_pause=True, 
            count_up=False, 
            end_siren=False, 
            last_minute_decimal=False, 
            reset_fouls=False, 
            show_time=False, 
            show_time_zero=True, 
            show_time_ticker=False, 
            decides_extra_time=True, 
            decides_penalties=False, 
            sort_order=4
        )
        first_half_extra_time = Period(
            id=5, 
            name="First half extra time", 
            display_name="First half ET", 
            length=5*minute, 
            description="", 
            auto_start=False, 
            can_pause=True, 
            count_up=False, 
            end_siren=True, 
            last_minute_decimal=True, 
            reset_fouls=False, 
            show_time=True, 
            show_time_zero=False, 
            show_time_ticker=True, 
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=5
        )
        second_half_extra_time = Period(
            id=6, 
            name="Second half extra time", 
            display_name="Second half ET", 
            length=5*minute, 
            description="", 
            auto_start=False, 
            can_pause=True, 
            count_up=False, 
            end_siren=True, 
            last_minute_decimal=True, 
            reset_fouls=False, 
            show_time=True, 
            show_time_zero=False, 
            show_time_ticker=True, 
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=6
        )
        full_time_extra_time = Period(
            id=7, 
            name="Full time extra time", 
            display_name="Full time ET", 
            length=15*second, 
            description="", 
            auto_start=True, 
            can_pause=True, 
            count_up=False, 
            end_siren=False, 
            last_minute_decimal=False, 
            reset_fouls=False, 
            show_time=False, 
            show_time_zero=True, 
            show_time_ticker=False, 
            decides_extra_time=False, 
            decides_penalties=True, 
            sort_order=7
        )
        penalties = Period(
            id=8,
            name="Penalties",
            display_name="Penalties",
            length=None,
            description="", 
            auto_start=False, 
            can_pause=True, 
            count_up=False, 
            end_siren=False, 
            last_minute_decimal=False, 
            reset_fouls=False, 
            show_time=False, 
            show_time_zero=False, 
            show_time_ticker=False, 
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=8
        ) 
        full_time = Period(
            id=9,
            name="Full time",
            display_name="Full time",
            length=5*minute,
            description="", 
            auto_start=False, 
            can_pause=True, 
            count_up=False, 
            end_siren=False, 
            last_minute_decimal=False, 
            reset_fouls=False, 
            show_time=False, 
            show_time_zero=False, 
            show_time_ticker=False, 
            decides_extra_time=False, 
            decides_penalties=False, 
            sort_order=9
        )
        periods = [pre_game, first_half, half_time, second_half, normal_full_time, first_half_extra_time, second_half_extra_time, full_time_extra_time, penalties, full_time]
    
        period_configuration = PeriodConfiguration(1, "F-League Standard", "Normal", 1*minute, "Standard F-League period configuration", periods)
        home_team = Team(1, 1, "Sala Time FC", "#7030A0", "SAL", "Sala Time FC")
        away_team = Team(2, 1, "South Brisbane Fury", "#000000", "SBF", "South Brisbane Fury")
        competition = Competition(1, "2025", "F-League", False, True, True)
        fixture = Fixture(1, competition, "Normal round", 1, home_team, 0, 0, away_team,
                        datetime.now()+timedelta(minutes=10), "Court B", 0, 0, period_configuration)
        fixture_queue = FixtureQueue([fixture])
        return fixture_queue


