#!/usr/bin/env python2.7
import numpy as np

def MathModel(td):
    X = np.zeros(shape=(len(td.Records), len(td.TeamsIndex)))
    Y = np.zeros(shape=(len(td.Records), 1))
    for i, it in enumerate(td.Records):
        X[i][it[0]] = 1
        X[i][it[1]] = -1
        Y[i][0] = it[2] - it[3]
    return np.mat(X), np.mat(Y)


def LearnPredictor(td):
    X, Y = MathModel(td)
    X_ = np.linalg.pinv(X)
    r = X_ * Y
    return r


def RankTeams(model):
    rLst = list(model.flat)
    return sorted(xrange(len(rLst)), key=lambda i: rLst[i], reverse=True)


def ApplyModel(model, td):
    X, Y = MathModel(td)
    predicts = X * model
    return list(predicts.flat), list((predicts - Y).flat)

