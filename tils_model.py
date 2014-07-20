#!/usr/bin/env python2.7
import json
import numpy as np

class TeamsData(object):
    
    def __init__(self, filename):
        self.LoadData(filename)

    def LoadData(self, filename):
        self.TeamsIndex = {}
        self.RevTeamsIndex = {}
        self.Records = []
        with open(filename) as reader:
            for ln in reader:
                it = json.loads(ln)
                self.Records.append((
                    self.GetTeamID(it["team1"], it["region"]), 
                    self.GetTeamID(it["team2"], it["region"]), 
                    eval(it["orig-score"])
                ))

    def GetTeamID(self, teamname, region=None):
        teamId = self.TeamsIndex.get(teamname, None)
        if teamId is None:
            teamId = self.TeamsIndex[teamname] = len(self.TeamsIndex)
            self.RevTeamsIndex[teamId] = teamname, region
        return teamId
       
    def GetTeamName(self, teamId):
        return self.RevTeamsIndex[teamId][0]

    def GetTeamRegion(self, teamId):
        return self.RevTeamsIndex[teamId][1]


def SolveModel(td):
    X = np.zeros(shape=(len(td.Records), len(td.TeamsIndex)))
    Y = np.zeros(shape=(len(td.Records), 1))
    for i, it in enumerate(td.Records):
        X[i][it[0]] = 1
        X[i][it[1]] = -1
        Y[i][0] = it[2]
    X_ = np.linalg.pinv(np.mat(X))
    r = X_ * np.mat(Y)
    rLst = list(r.flat)
    rank = sorted(xrange(len(rLst)), key=lambda i: rLst[i], reverse=True)
    for i in rank:
        print "{0}\t{1}\t{2}\t{3}".format(i, td.GetTeamName(i).encode("utf-8"), td.GetTeamRegion(i), rLst[i])


if __name__ == "__main__":
    td = TeamsData("result.js")
    SolveModel(td)
