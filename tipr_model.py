#!/usr/bin/env python2.7
import numpy as np

def MathModel(td):
    T, N = len(td.TeamsIndex), len(td.Records)
    X = np.zeros(shape=(2 * N, 2 + 2 * T))
    Y = np.zeros(shape=(2 * N, 1))
    for i, it in enumerate(td.Records):
        X[i][0] = X[i][2 + it[0]] = X[i][2 + T + it[1]] = 1
        X[i + N][1] = X[i + N][2 + it[1]] = X[i + N][2 + T + it[0]] = 1
        Y[i] = it[2]
        Y[i + N] = it[3]
    return np.mat(X), np.mat(Y)


def SubLearn(r, X, Y, indices):
    r[indices] = 0
    b = X * r
    c = X.T[indices] * Y
    r[indices] = np.log(c) - np.log(X.T[indices] * np.exp(b))


def LearnPredictor(td):
    EPS = 1e-4
    T, N = len(td.TeamsIndex), len(td.Records)
    X, Y = MathModel(td)

    r = np.array(np.random.random(size=2 + 2 * T))
    filters = np.array((Y.T * X == 0)).reshape(2 + 2 * T)
    r = np.mat(
        (1 - filters) * r 
        - (filters & [2 <= i < 2 + T for i in xrange(2 + 2 * T)]) * 10
        - (filters & [2 + T <= i < 2 + 2 * T for i in xrange(2 + 2 * T)]) * 10
    ).T
    for _it in xrange(1000):
        _r = r.copy()
        SubLearn(r, X, Y, ~filters & [2 <= i < 2 + T for i in xrange(2 + 2 * T)])
        SubLearn(r, X, Y, ~filters & [2 + T <= i < 2 + 2 * T for i in xrange(2 + 2 * T)])
        SubLearn(r, X, Y, ~filters & [0 <= i < 2 for i in xrange(2 + 2 * T)])
        _diff = np.sqrt((_r - r).T * (_r - r))
        print _diff, _it
        if _diff < EPS:
            break
    
    print "Attack forces"
    rLst = sorted(xrange(T), key=lambda i: r[2 + i], reverse=True)
    with open("ranking.tipr_model.attack", "w") as rnk_pr:
        print >>rnk_pr, u"\n".join(u"{0}\t{1}\t{2}".format(td.GetTeamName(i), td.GetTeamRegion(i), r[2 + i]) for i in rLst).encode("utf-8")

    print 
    print "Defence forces"
    rLst = sorted(xrange(T), key=lambda i: r[2 + T + i])
    with open("ranking.tipr_model.defence", "w") as rnk_pr:
        print >>rnk_pr, u"\n".join(u"{0}\t{1}\t{2}".format(td.GetTeamName(i), td.GetTeamRegion(i), r[2 + T + i]) for i in rLst).encode("utf-8")
