import requests
import json
import datetime

"""
Function to fetch fixtures from Squadi API
Parameters:
    organisation_id: int, default 716
    hours_from_now: int, default 12

Returns: JSON dict of fixtures at organisation_id within hours_from_now
"""
def fetch_fixtures_json(organisation_id: int = 716, hours_from_now: int = 36):
    time_now = datetime.datetime.now(datetime.timezone.utc)
    time_end = time_now + datetime.timedelta(hours=hours_from_now)
    url = 'https://api.squadi.com/livescores/matches/getAllMatches'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
    }
    payload = {
        "competitionIds": "[-1]",
        "venueIds": "[-1]",
        "offset": 0,
        "limit": 1000,
        "showOnlyOwnedMatches": True,
        "sortBy": None,
        "sortOrder": None,
        "from": time_now.isoformat(),
        "to": time_end.isoformat(),
        "organisationId": organisation_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def get_timeslots(fixtures):
    timeslots = list()
    for fixture in fixtures['matches']:
        start_time = fixture['startTime']
        if start_time not in timeslots:
            timeslots.append(fixture['startTime'])
    timeslots.sort()
    return timeslots

def create_squadi_buzzer_json(timeslots: list, half_length: int = 18, break_length: int = 2):
    buzzer_json = dict()
    buzzer_json['timeslots'] = timeslots
    buzzer_json['half_length'] = half_length
    buzzer_json['break_length'] = break_length
    return buzzer_json