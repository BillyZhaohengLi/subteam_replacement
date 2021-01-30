import numpy as np
import networkx as nx
import string
import random
import queue
import math
import copy
import datetime
import scipy.sparse
import sys
import scipy
from itertools import combinations
from utils import *

## helper function based off teamrep_fast_exact; returns 1 most suitable team member to add to remainTeam.
## adj: unnormalized adjacency matrix
## L_diag_columns: array of size l, each cell is the diagonalized ith column in skill matrix
## currentTeam: original team, untouched
## remainTeam: current intermediate state of new team
## c: restart probability
def teamrep_fast_exact_node_labeled(adj, L, c, currentTeam, remainTeam, checksum = None):
    ## Put each diagonalized column into 1 cell
    L_diag_columns = []
    for i in range(L.shape[1]):
        L_diag_columns.append(scipy.sparse.csr_matrix(scipy.sparse.diags(L[:,i])))

    n = adj.shape[1]
    dn = len(L_diag_columns)
    ##print("base team: " + str(currentTeam))
    ##print("current team: " + str(remainTeam))

    W = adj[np.ix_(currentTeam, currentTeam)].todense()
    np.fill_diagonal(W, 0)

    n0 = len(currentTeam)
    W0 = np.zeros((n0, n0))
    W0[:len(remainTeam), :len(remainTeam)] = adj[np.ix_(remainTeam, remainTeam)].todense()
    np.fill_diagonal(W0, 0)

    L = []
    for i in range(dn):
        L.append(L_diag_columns[i][np.ix_(currentTeam, currentTeam)].todense())

    L0 = []
    for i in range(dn):
        temp = np.zeros((n0, n0))
        temp[:len(remainTeam), :len(remainTeam)] = L_diag_columns[i][np.ix_(remainTeam,remainTeam)].todense()
        L0.append(temp)

    q = np.ones((n0, 1)) / n0
    p = np.ones((n0, 1)) / n0
    qx = np.kron(q,q)
    px = np.kron(p,p)

    temp = np.zeros((n0*n0, n0*n0))
    for i in range(dn):
        temp += np.kron(np.matmul(L[i], W), np.matmul(L0[i], W0))
    invZ = np.linalg.inv(np.identity(n0*n0) - c * temp)

    R = np.zeros((n0*n0,1))
    for i in range(dn):
        R += np.kron(L[i].dot(p), L0[i].dot(p))

    base = np.linalg.multi_dot([np.transpose(qx), invZ, R])
    l = c * np.matmul(np.transpose(qx), invZ)
    r = np.matmul(invZ, R)

    candidates = diff(diff(list(range(n)), currentTeam), remainTeam)
    candidates = np.array(candidates)[np.asarray((np.sum(adj[np.ix_(candidates, remainTeam)], axis = 1) > 0)).squeeze()]
    ## print("candidates: " + str(candidates))

    score = {}
    for i in candidates:
        try:
            i = i[0]
        except:
            pass

        s = np.zeros((1, n0))
        s[(0, len(remainTeam))] = 1

        t = np.zeros((1, n0))
        temp2 = adj[np.ix_([i],remainTeam)].todense()
        t[:temp2.shape[0], :temp2.shape[1]] = temp2

        A = np.concatenate((np.transpose(t), np.transpose(s)), axis=1)
        B = np.concatenate((s, t), axis=0)

        a = np.transpose(s)
        b = []
        for j in range(dn):
            temp = np.zeros((1, n0))
            temp[(0, len(remainTeam))] = L_diag_columns[j][(i, i)]
            b.append(temp)

        A1 = np.kron(L[0], a)
        B1 = np.kron(np.identity(n0), b[0])
        for j in range(1, dn):
            A1 = np.concatenate((A1, np.kron(L[j], a)), axis = 1)
            B1 = np.concatenate((B1, np.kron(np.identity(n0), b[j])), axis = 0)

        X1 = np.zeros((n0*n0,n0*2))
        X2 = np.zeros((n0*n0,n0*2))
        for j in range(dn):
            X1 += np.kron(np.matmul(L[j], W), np.matmul(L0[j], A))
            X2 += np.kron(np.matmul(L[j], W), np.linalg.multi_dot([a, b[j], A]))

        Y1 = np.matmul(B1, np.kron(W, W0))
        Y2 = np.kron(np.identity(n0), B)

        X = np.concatenate((A1, X1, X2), axis = 1)
        Y = np.concatenate((Y1, Y2, Y2), axis = 0)

        M = np.linalg.inv(np.identity((dn+4)*n0) - c * np.linalg.multi_dot([Y, invZ, X]))
        r0 = np.linalg.multi_dot([invZ, A1, B1, px])

        score[i] = base + np.linalg.multi_dot([np.transpose(qx), r0]) + np.linalg.multi_dot([l, X, M, Y, (r+r0)])

    #print(sorted(list(score.items()), key=lambda x:x[1]))
    #print(len(score))
    if len(score) == 0: ## or max(score, key=score.get) == 0:
        return None
    else:
        sorted_score = sorted(score.items(), key=lambda x:x[1], reverse=True)
        ## print(sorted_score)
        return sorted_score
