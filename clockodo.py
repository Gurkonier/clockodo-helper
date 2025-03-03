import json
import os
import sys
from datetime import datetime, timedelta

import click
import requests
from requests.auth import HTTPBasicAuth

config_dir = os.path.expanduser("~") + "/.clockodo/"
filename = "settings.json"

api_url = "https://my.clockodo.com/api/"
application_name = "Clockodo Helper"

@click.command()
@click.argument('email')
@click.argument('apikey')
def api_key(email: str, apikey: str):
    os.makedirs(config_dir, exist_ok=True)
    print(config_dir)
    with open(config_dir+filename, "w") as config_file:
        config_file.write(json.dumps({
            "email": email,
            "key": apikey
        }))

def load_api_key() -> dict:
    if not os.path.exists(config_dir + filename):
        print("API Key not available")
        sys.exit(4)
    with open(config_dir+filename) as config_file:
        return json.loads(config_file.read())

@click.command()
@click.argument("days", nargs=-1, type=click.IntRange(min=0, max=6))
def home_office(days: tuple[int]):
    key = load_api_key()

    selected: list[datetime] = []
    today = datetime.now()
    print("Do you want to add the following home office days:")
    for day in days:
        new = today+timedelta(days=(7-today.weekday())+day)
        selected.append(new)
        print(new.strftime("%a %d.%m.%Y"))
    click.echo('Continue? [yn] ', nl=False)
    c = click.getchar()
    click.echo()
    if c == 'y':
        add_home_office_days(key, [day.strftime("%Y-%m-%d") for day in selected])
    elif c == 'n':
        click.echo('Abort!')
        exit(0)
    else:
        click.echo('Invalid input. Aborted!')
        exit(0)

def add_home_office_days(api_key: dict, dates: list[str]):
    for date in dates:
        requests.post(
            url=api_url+"absences",
            headers={
                "X-Clockodo-External-Application": f"{application_name};{api_key["email"]}"
            },
            auth=HTTPBasicAuth(api_key["email"], api_key["key"]),
            params={
                "date_since": date,
                "date_until": date,
                "type": 8
            }
        )

@click.group()
def commands():
    pass

commands.add_command(api_key)
commands.add_command(home_office)

if __name__=="__main__":
    commands()
