#!/usr/bin/env python2.7
import json
import tils_model

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
        self.LoadData(filename)

    def LoadData(self, filename):
        self.TeamsIndex = {}
        self.Teams = []
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


if __name__ == "__main__":
    td = TeamsData("wc2014q-result.js")
    model = tils_model.LearnPredictor(td)
    predicts, err = tils_model.ApplyModel(model, td)
    ShowErrors(err)
    
