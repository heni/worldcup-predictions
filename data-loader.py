#!/usr/bin/env python2.7
import json
import re
import urllib2
from bs4 import BeautifulSoup

def LoadData(url):
    events = []
    partIDS = ["Europe", "South America", "Africa", "Asia", "North/Central America", "Oceania"]
    doc = BeautifulSoup(urllib2.urlopen(url))
    for idx, part in enumerate(doc.select("pre")):
        for ln in part.text.split("\n"):
            if len(ln) >= 44 and (ln[8] == ln[24] == ln[42] == " " and ln[38] == " " or ln[37] == " "):
                date = ln[:8].strip()
                city = ln[9:24].strip()
                if ln[38] == " ":
                    team1 = ln[25:38].strip().lower()
                    scores = ln[39:42].strip()
                elif ln[37] == " ":
                    team1 = ln[25:37].strip().lower()
                    scores = ln[38:42].strip()
                else:
                    raise RuntimeError("format error")
                rest = ln[43:].strip().lower()
                cmtRes = re.search("\[(.*)\]", rest)
                if cmtRes:
                    team2 = rest[:cmtRes.start()].strip()
                    comment = cmtRes.group(1)
                else:
                    team2 = rest.strip()
                    comment = None
                events.append({
                    "region": partIDS[idx],
                    "team1": team1,
                    "team2": team2,
                    "score": scores,
                    "match-place": city,
                    "match-date": date,
                    "comment": comment
                })
            else:
                #print ln.encode("utf-8")
                pass
    return events

if __name__ == "__main__":
    events = LoadData("http://www.rsssf.com/tables/2014q.html")
    for ev in events:
        print json.dumps(ev)
