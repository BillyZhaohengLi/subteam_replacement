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

## Kronecker product of sum of diagonalized columns L1 and L2
def diag_kron(L1, L2):
    n = L1.shape[0]
    l = L2.shape[0]
    x = L1.shape[1]
    Lx = np.zeros((n * l, n* l))
    for k in range(x):
        Lx = np.add(Lx, np.kron(np.diag(L1[:,k]), np.diag(L2[:,k])))
    return Lx

## Random walk node-labeled graph kernel
def node_labeled_kernel(A, L, c, team_1, team_2, sum = False):
    t1 = len(team_1)
    t2 = len(team_2)

    q1 = np.ones((t1, 1)) / t1
    p1 = np.ones((t1, 1)) / t1
    q2 = np.ones((t2, 1)) / t2
    p2 = np.ones((t2, 1)) / t2

    qx = np.kron(q1, q2)
    px = np.kron(p1, p2)

    A1 = A[np.ix_(team_1, team_1)].todense()
    np.fill_diagonal(A1, 0)
    L1 = L[np.ix_(team_1, list(range(L.shape[1])))]

    A2 = A[np.ix_(team_2, team_2)].todense()
    np.fill_diagonal(A1, 0)
    L2 = L[np.ix_(team_2, list(range(L.shape[1])))]

    Lx = diag_kron(L1, L2)
    Ax = np.kron(A1, A2)

    if sum:
        return np.sum(np.matmul(inv(np.identity(t1 * t2) - c * np.matmul(Lx, Ax)), Lx)) / (t1 ** 4)
    else:
        return multi_dot([np.transpose(px), inv(np.identity(t1 * t2) - c * np.matmul(Lx, Ax)), Lx, qx]).item(0,0)
