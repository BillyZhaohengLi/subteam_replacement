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
from itertools import combinations
from numpy.linalg import inv
from numpy.linalg import multi_dot

diff = lambda l1,l2: [x for x in l1 if x not in l2]

## Returns most suitable person to insert given current and remaining teams.
## A: unnormalized adjacency matrix
## L: array of size l * n, each row is skill matrix of 1 person
## W: skill adjacnecy matrix, weighs importance of skill combinations
## c: restart probability
## current_team: original team T
## remaining_team: remaining team T - p
def find_best_person(A, L, W, c, current_team, remaining_team):
    l = W.shape[0]
    t1 = len(current_team)
    t2 = len(remaining_team)

    q1 = np.ones((t1, 1)) / t1
    p1 = np.ones((t1, 1)) / t1
    q2 = np.ones((t2 + 1, 1)) / (t2 + 1)
    p2 = np.ones((t2 + 1, 1)) / (t2 + 1)

    qx = np.kron(q1,q2)
    px = np.kron(p1,p2)

    ## subgraph of current team T
    A1 = A[np.ix_(current_team, current_team)].todense()
    np.fill_diagonal(A1, 0)
    L1 = L[np.ix_(current_team, list(range(L.shape[1])))]

    ## subgraph of remaining team T - p
    Ac = A[np.ix_(remaining_team, remaining_team)].todense()
    np.fill_diagonal(A1, 0)
    Lc = L[np.ix_(remaining_team, list(range(L.shape[1])))]

    Z = [[None for i in range(l)] for j in range(l)]
    ## precompute invariant Z tensor
    for m in range(l):
        for n in range(m + 1):
            E1 = W[m][n] * np.maximum(np.matmul(L1[:,m,None], np.transpose(L1[:,n,None])), np.matmul(L1[:,n,None], np.transpose(L1[:,m,None])))
            Z[m][n] = np.multiply(E1, A1)

    ## precompute Ablock = I-cY(kron)Z and Dblock = I
    Ablock = np.identity(t1 * t2)
    for m in range(l):
        for n in range(m + 1):
            Ec = np.maximum(np.matmul(Lc[:,m,None], np.transpose(Lc[:,n,None])), np.matmul(Lc[:,n,None], np.transpose(Lc[:,m,None])))
            Y = np.multiply(Ec, Ac)
            Ablock -= c * np.kron(Y, Z[m][n])

    Ablock_inv = inv(Ablock)
    Dblock = np.identity(t1)

    ## prune non-conncected candidates
    candidates = diff(list(range(A.shape[0])), current_team + remaining_team)
    candidates = np.array(candidates)[np.asarray((np.sum(A[np.ix_(candidates, remaining_team)], axis = 1) > 0)).squeeze()]
    candidates = diff(candidates, current_team + remaining_team)

    score = {}
    for candidate in candidates:
        Ld1 = L[np.ix_([candidate], list(range(L.shape[1])))]
        Ad2 = A[np.ix_(remaining_team, [candidate])].todense()

        ## compute B & C blocks
        Bblock = np.zeros((t1 * t2, t1))
        for m in range(l):
            for n in range(m + 1):
                Ed1 = np.maximum(Lc[:,m,None] * Ld1[:,n], Lc[:,n,None] * Ld1[:,m])
                X = np.multiply(Ed1, Ad2)
                Bblock -= c * np.kron(X, Z[m][n])

        Cblock = np.transpose(Bblock)

        ## Sherman-morrison
        newD = inv(Dblock - multi_dot([Cblock, Ablock_inv, Bblock]))

        newA = Ablock_inv + multi_dot([Ablock_inv, Bblock, newD, Cblock, Ablock_inv])
        newB = -multi_dot([Ablock_inv, Bblock, newD])
        newC = -multi_dot([newD, Cblock, Ablock_inv])

        kernel_inv = np.block([[newA, newB], [newC, newD]])

        ## Compute score
        score[candidate] = multi_dot([np.transpose(px), kernel_inv, qx]).item(0,0)

    ## No suitable candidate
    if len(score) == 0:
        return None
    else:
        sorted_score = sorted(score.items(), key=lambda x:x[1], reverse=True)
        return max(score, key=score.get), score[max(score, key=score.get)]
