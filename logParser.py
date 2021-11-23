import datetime
import time
import re
from dataclasses import dataclass


def timedif(line1, line2):
    regex = "(\d{2})\/(\d{2})\/(\d{4}) - (\d*):(\d*):(\d*)"
    m = list(map(int, re.findall(regex, line1)[0]))
    n = list(map(int, re.findall(regex, line2)[0]))
    d = datetime.datetime(m[2], m[0], m[1], m[3], m[4], m[5])
    f = datetime.datetime(n[2], n[0], n[1], n[3], n[4], n[5])
    return int(time.mktime(f.timetuple()) - time.mktime(d.timetuple()))


def timeplayed(lines, steamid):
    valids = []
    round_started = False
    for line in lines:
        if "Round_Start" in line:
            round_started = True
        if "Round_Win" in line:
            round_started = False
        if steamid in line and round_started:
            valids.append(line)
    return timedif(valids[0], valids[-1])


@dataclass()
class Team:
    side: str
    score: int = 0
    kills: int = 0
    deaths: int = 0
    damage: int = 0
    charges: int = 0
    drops: int = 0
    firstcaps: int = 0
    caps: int = 0


@dataclass()
class Player:
    side: str
    steamid: str
    name: str
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    suicides: int = 0
    kadr: float = 0
    kdr: float = 0
    damage: int = 0
    damage_taken: int = 0
    heals_received: int = 0
    longest_killstreak: int = 0
    airshots: int = 0
    dpm: int = 0
    ubers: int = 0
    drops: int = 0
    medkits: int = 0
    medkits_hp: int = 0
    backstabs: int = 0
    headshots: int = 0
    sentries: int = 0
    heal: int = 0
    caps: int = 0
    intel_caps: int = 0
    time_played: int = 0


@dataclass()
class SteamID:
    text: str
    name: str


def parse(logfile):
    with open(logfile, 'r', encoding="utf8") as file:
        lines = file.readlines()
        for line in reversed(lines):
            if "Round_Win" in line:
                endline = line
                break
        total_length = timedif(lines[0], endline)
        round_over = True
        startline = lines[0]
        players = []
        steamids = []
        Red = Team("Red")
        Blue = Team("Blue")
        for index, line in enumerate(lines):
            if re.search("\"Round_Win\" \(winner \"(\w*)\"\)", line) != None and "pointcaptured" in lines[index - 1]:
                m = re.search("\"Round_Win\" \(winner \"(\w*)\"\)", line)
                if m.group(1) == "Blue":
                    Blue.score += 1
                elif m.group(1) == "Red":
                    Red.score += 1
            if "Round_Win" in line:
                round_over = True
                startline = line
            if "Round_Start" in line:
                mid_capped = False
                round_over = False
                total_length -= timedif(startline, line)
            if "killed" in line and not round_over:
                regex = "\"([^\"]*)<(\d*)><(\[U:[10]:\d*\])><(\w*)>\""
                m = re.findall(regex, line)
                if m[0][3] == "Blue":
                    Blue.kills += 1
                elif m[0][3] == "Red":
                    Red.kills += 1
                if m[1][3] == "Red":
                    Red.deaths += 1
                elif m[1][3] == "Blue":
                    Blue.deaths += 1
            if "committed suicide with" in line and not round_over:
                regex = "\"([^\"]*)<(\d*)><(\[U:[10]:\d*\])><(\w*)>\""
                m = re.search(regex, line)
                if m.group(4) == "Blue":
                    Blue.deaths += 1
                elif m.group(4) == "Red":
                    Red.deaths += 1
            if "triggered \"damage\" against" in line and not round_over:
                regex = "\(damage \"(\d*)\"\)"
                m = re.search(regex, line)
                r = "\"([^\"]*)<(\d*)><(\[U:[10]:\d*\])><(\w*)>\""
                n = re.findall(r, line)
                if n[0][3] == "Blue":
                    Blue.damage += int(m.group(1))
                elif n[0][3] == "Red":
                    Red.damage += int(m.group(1))  
            if "triggered \"chargedeployed\"" in line and not round_over:
                regex = "\"([^\"]*)<(\d*)><(\[U:[10]:\d*\])><(\w*)>\""
                m = re.search(regex, line)
                if m.group(4) == "Blue":
                    Blue.charges += 1
                elif m.group(4) == "Red":
                    Red.charges += 1
            if "triggered \"medic_death\" against" in line and not round_over:
                r = "\(ubercharge \"(\d)\"\)"
                n = re.search(r, line)
                if n:
                    regex = "\"([^\"]*)<(\d*)><(\[U:[10]:\d*\])><(\w*)>\""
                    m = re.findall(regex, line)
                    if m[1][3] == "Blue":
                        if int(n.group(1)) == 1:
                            Blue.drops += 1
                    elif m[1][3] == "Red":
                        if int(n.group(1)) == 1:
                            Red.drops += 1           
            if "triggered \"pointcaptured\"" in line and not round_over:
                regex = "Team \"(\w*)\" triggered \"pointcaptured\" \(cp \"(\d)\"\)"
                m = re.search(regex, line)
                if m.group(1) == "Blue":
                    Blue.caps += 1
                    if m.group(2) == "2" and not mid_capped:
                        mid_capped = True
                        Blue.firstcaps += 1
                elif m.group(1) == "Red":
                    Red.caps += 1
                    if m.group(2) == "2" and not mid_capped:
                        mid_capped = True
                        Red.firstcaps += 1
            if "spawned as" in line and not "\"undefined\"" in line:
                regex = "\"([^\"]*)<(\d*)><(\[U:[10]:\d*\])><(\w*)>\""
                m = re.search(regex, line)
                n = re.search("\[U:\d:(\d*)\]", m.group(3))
                steamid = SteamID(m.group(3), m.group(1))
                if not steamid in steamids:
                    steamids.append(steamid)
                    exec(
                        f"_{n.group(1)} = Player(\"{m.group(4)}\",\"{m.group(3)}\",\"{m.group(1)}\")\nplayers.append(_{n.group(1)})")
        print(Red)
        print(Blue)
        #for player in players:
            #print(player)
        #print(timeplayed(lines, "[U:1:83749997]"))
        #print(total_length)