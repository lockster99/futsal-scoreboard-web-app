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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Content-type': 'application/json; charset=UTF-8',
    }
    payload = {
        "competitionIds": "[-1]",
        "venueIds": "[1236]",
        "offset": 0,
        "limit": 1000,
        "showOnlyOwnedMatches": False,
        "sortBy": None,
        "sortOrder": None,
        "from": "2025-11-07T14:00:00.000Z",
        "to": "2025-11-08T13:59:59.059Z",
        "organisationId": organisation_id
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def filter_fixtures_json_by_court(fixtures, court_number=1):
    filtered_fixtures = dict()
    filtered_fixtures['matches'] = list()
    for fixture in fixtures['matches']:
        if fixture['venueCourt']['courtNumber'] == court_number:
            filtered_fixtures['matches'].append(fixture)
    return filtered_fixtures


def get_team_logos_from_squadi(competition_id: int = 1153):
    url = f'https://api.squadi.com/livescores/teams/list?competitionId={competition_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Content-Type': 'application/json; charset=UTF-8',
    }
    response = requests.get(url, headers=headers)
    teams_json = response.json()
    team_logos = set()
    for team in teams_json:
        if team['logoUrl'] != team['linkedCompetitionOrganisation']['logoUrl'] or competition_id == 1096:
            team_logos.add(team['name'])
    return team_logos


def download_image(url, filename):
    """
    Downloads an image from a given URL and saves it to a specified filename.

    Args:
        url (str): The URL of the image to download.
        filename (str): The local path and filename to save the image as.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Image downloaded successfully to {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")


def download_team_logos(competition_id: int = 1153):
    logo_urls = get_team_logos_from_squadi(competition_id)
    for team_name, logo_url in logo_urls.items():
        download_image(logo_url, f"static/img/{team_name}-logo.png")


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


#print(filter_fixtures_json_by_court(fetch_fixtures_json(), court_number=2))