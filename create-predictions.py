#!/usr/bin/env python2.7
import json
import re
import tils_model, tipr_model

class TeamInfo(object):
    def __init__(self, teamname):
        self.Name = teamname
        self.RegCounters = {}

    def CountRegion(self, region):
        self.RegCounters[region] = self.RegCounters.get(region, 0) + 1
    
    def GetName(self):
        return self.Name

    def GetRegion(self):
        return max(self.RegCounters, key=self.RegCounters.get)


class TeamsData(object):
    
    def __init__(self, filename):
        self.TeamsIndex = {}
        self.Teams = []
        self.Records = []
        self.UpdateData(filename)

    def UpdateData(self, filename):
        with open(filename) as reader:
            for ln in reader:
                it = json.loads(ln)
                g1, g2 = map(int, re.findall("\d+", it["orig-score"]))
                self.Records.append((
                    self.GetTeamID(it["team1"], it["region"]), 
                    self.GetTeamID(it["team2"], it["region"]), 
                    g1, g2,
                ))

    def GetTeamID(self, teamname, region=None):
        teamId = self.TeamsIndex.get(teamname, None)
        if teamId is None:
            teamId = self.TeamsIndex[teamname] = len(self.Teams)
            self.Teams.append(TeamInfo(teamname))
        if region:
            self.Teams[teamId].CountRegion(region)
        return teamId
       
    def GetTeamName(self, teamId):
        return self.Teams[teamId].GetName()

    def GetTeamRegion(self, teamId):
        return self.Teams[teamId].GetRegion()


def ShowErrors(err):
    import matplotlib.pyplot as plt
    plt.hist(err, bins=20)
    plt.show()


def PrintRanks(alg, model, td):
    for tId in alg.RankTeams(model):
        print u"{0}\t{1}\t{2}\t{3}".format(tId, td.GetTeamName(tId), td.GetTeamRegion(tId), next(model[tId].flat)).encode("utf-8")


if __name__ == "__main__":
    #td = TeamsData("eu2012-result.js")
    #td.UpdateData("wc2014q-result.js")
    td = TeamsData("wc2014q-result.js")
    model = tipr_model.LearnPredictor(td)
    #PrintRanks(tils_model, model, td)
    #predicts, err = tils_model.ApplyModel(model, td)
    #ShowErrors(err)
    
