#!/usr/bin/env python2.7
# coding: utf-8
import json
import re
import sys
import urllib2
from bs4 import BeautifulSoup

SHOW_BAD_LINES = True
def LogBadLine(ln):
    if SHOW_BAD_LINES:
        print >>sys.stderr, "bad line:", ln.encode("utf-8")

Reductions = {
    u"afr.": u"african",
    u"am.": u"american",
    u"antigua/b.": u"antigua and barbuda",
    u"antigua/barb.": u"antigua and barbuda",
    u"herz.": u"herzegovina",
    u"herzeg.": u"herzegovina",
    u"bosnia & ": u"bosnia-",
    u"br.": u"british",
    u"brazz.": u"brazzaville",
    u"virgin i.": u"virgin islands",
    u"c.": u"central",
    u"equat.": u"equatorial",
    u"isl.": u"islands",
    u"kinsh.": u"kinshasa",
    u"n. ireland": u"northern ireland",
    u"papua n.g.": u"papua new guinea",
    u"săo tomé/pr.": u"săo tomé e príncipe",
    u"st. kitts/n.": u"saint kitts and nevis",
    u"st.vincent/g.": u"saint vincent and the grenadines",
    u"trinidad/tob.": u"trinidad and tobago",
    u"turks/caicos": u"turks and caicos islands",
    u"r.": u"republic",
    u"rep.": u"republic",
}

def NormalizeCoutryName(name):
    _name = name.strip().lower()
    while re.search("[\./&]", _name):
        avail_r = filter(lambda _f: _f in _name, Reductions)
        if not avail_r:
            raise RuntimeError(u"can't normalize country name: {0}".format(name).encode("utf-8"))
        best_r = max(avail_r, key=len)
        _name = _name.replace(best_r, Reductions[best_r])
    return _name


def LoadData_wc2014q(url):
    events = []
    partIDS = ["Europe", "South America", "Africa", "Asia", "North/Central America", "Oceania"]
    doc = BeautifulSoup(urllib2.urlopen(url))
    for idx, part in enumerate(doc.select("pre")):
        for ln in part.text.split("\n"):
            if len(ln) >= 44 and (ln[8] == ln[24] == ln[42] == " " and ln[38] == " " or ln[37] == " "):
                date = ln[:8].strip()
                city = ln[9:24].strip()
                if ln[38] == " ":
                    team1 = NormalizeCoutryName(ln[25:38].strip())
                    scores = ln[39:42].strip()
                elif ln[37] == " ":
                    team1 = NormalizeCoutryName(ln[25:37].strip())
                    scores = ln[38:42].strip()
                else:
                    raise RuntimeError("format error")
                if not re.search("\d+-\d+|o/w|w/o|awd", scores):
                    LogBadLine(ln)
                    continue
                rest = ln[43:].strip().lower()
                cmtRes = re.search("\[(.*)\]", rest)
                if cmtRes:
                    team2 = NormalizeCoutryName(rest[:cmtRes.start()].strip())
                    comment = cmtRes.group(1)
                else:
                    team2 = NormalizeCoutryName(rest.strip())
                    comment = None
                if re.search("o/w|w/o|awd", scores):
                    if not comment:
                        LogBadLine(ln)
                        continue
                    awd_score = re.search("awarded\s+(\d+-\d+)[;,]", comment).group(1)
                    orig_score = re.search("(?:originally|abandoned at)\s+(\d+-\d+)", comment).group(1)
                    scores = awd_score, orig_score
                events.append({
                    "region": partIDS[idx],
                    "team1": team1,
                    "team2": team2,
                    "orig-score": scores if isinstance(scores, (str, unicode)) else scores[1],
                    "awd-score": scores if isinstance(scores, (str, unicode)) else scores[0],
                    "match-place": city,
                    "match-date": date,
                    "comment": comment
                })
            else:
                #print ln.encode("utf-8")
                pass
    return events


def ParseRest(restStr):
    cmtRes = re.search("\[([^]]+)\]", restStr)
    if cmtRes:
        team = NormalizeCoutryName(restStr[:cmtRes.start()])
        comment = re.findall("\[([^]]+)\]",restStr) 
        if len(comment) == 1:
            comment = comment[0]
    else:
        team = NormalizeCoutryName(restStr)
        comment = None
    return team, comment


def LoadData_eu2012(url):
    events = []
    partIDS = ["Qualifying Stage", "Final Tournament"]
    doc = BeautifulSoup(urllib2.urlopen(url))
    for idx, part in enumerate(doc.select("pre")):
        for ln in part.text.split("\n"):
            if len(ln) >= 33 and (ln[2] == ln[6] == ln[11] == ln[28] == ln[32] == " ") and "[" not in ln[:33]:
                date = ln[:11]
                team1 = NormalizeCoutryName(ln[12:28])
                scores = ln[29:32].strip().replace(u"\x96", "-")
                team2, comment = ParseRest(ln[33:])
                events.append({
                    "region": "Europe",
                    "stage": partIDS[idx],
                    "team1": team1,
                    "team2": team2,
                    "orig-score": scores,
                    "match-date": date,
                    "comment": comment,
                })
            else:
                #print ln.encode("utf-8")
                pass
    return events


Loaders = {
    "wc2014q": LoadData_wc2014q,
    "eu2012": LoadData_eu2012,
}

def Process(url, outFile, fmt):
    with open(outFile, "w") as res_pr:
        for ev in Loaders[fmt](url):
            print >>res_pr, json.dumps(ev)


if __name__ == "__main__":
    pass
    #Process("http://www.rsssf.com/tables/2014q.html", "wc2014q-result.js", "wc2014q")
    #Process("http://www.rsssf.com/tables/2012e.html", "eu2012-result.js", "eu2012")

