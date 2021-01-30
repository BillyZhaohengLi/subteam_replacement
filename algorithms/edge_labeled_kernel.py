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

## Computes edge-labeled kernel by definition; an edge attribute is generated for each permutation of skill pair
## Sum: returns average of matrix elements according to approximate kernel definition.
def edge_labeled_kernel(A, L, W, c, team_1, team_2, sum = False):
    l = W.shape[0]
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

    Ex = np.zeros((t1 * t2, t1 * t2))

    for m in range(l):
        for n in range(l):
            E1 = np.matmul(L1[:,m,None], np.transpose(L1[:,n,None]))
            E2 = np.matmul(L2[:,m,None], np.transpose(L2[:,n,None]))
            Ex += W[m][n] * np.kron(E1, E2)

    Ax = np.kron(A1, A2)

    if sum:
        return np.sum(inv(np.identity(t1 * t2) - c * np.multiply(Ex, Ax))) / (t1 ** 4)
    else:
        return multi_dot([np.transpose(px), inv(np.identity(t1 * t2) - c * np.multiply(Ex, Ax)), qx]).item(0,0)

## Experimental version
## Computes edge-labeled kernel, but compute edge attributes using skill combinations.
## Sum: returns average of matrix elements according to approximate kernel definition.
def edge_labeled_kernel_undirected(A, L, W, c, team_1, team_2, sum = False):
    l = W.shape[0]
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

    Ex = np.zeros((t1 * t2, t1 * t2))

    for m in range(l):
        for n in range(m + 1):
            E1 = np.matmul(L1[:,m,None], np.transpose(L1[:,n,None])) + np.matmul(L1[:,n,None], np.transpose(L1[:,m,None]))
            E2 = np.matmul(L2[:,m,None], np.transpose(L2[:,n,None])) + np.matmul(L2[:,n,None], np.transpose(L2[:,m,None]))
            Ex += W[m][n] * np.kron(E1, E2)

    Ax = np.kron(A1, A2)

    if sum:
        return np.sum(inv(np.identity(t1 * t2) - c * np.multiply(Ex, Ax))) / (t1 ** 4)
    else:
        return multi_dot([np.transpose(px), inv(np.identity(t1 * t2) - c * np.multiply(Ex, Ax)), qx]).item(0,0)

## Computes edge-labeled kernel by definition in paper section 3.1
## Sum: returns average of matrix elements according to approximate kernel definition.
def edge_labeled_kernel_argmax(A, L, W, c, team_1, team_2, sum = False):
    l = W.shape[0]
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

    Ex = np.zeros((t1 * t2, t1 * t2))

    for m in range(l):
        for n in range(m + 1):
            E1 = np.maximum(np.matmul(L1[:,m,None], np.transpose(L1[:,n,None])), np.matmul(L1[:,n,None], np.transpose(L1[:,m,None])))
            E2 = np.maximum(np.matmul(L2[:,m,None], np.transpose(L2[:,n,None])), np.matmul(L2[:,n,None], np.transpose(L2[:,m,None])))
            Ex += W[m][n] * np.kron(E1, E2)

    Ax = np.kron(A1, A2)

    if sum:
        return np.sum(inv(np.identity(t1 * t2) - c * np.multiply(Ex, Ax))) / (t1 ** 4)
    else:
        return multi_dot([np.transpose(px), inv(np.identity(t1 * t2) - c * np.multiply(Ex, Ax)), qx]).item(0,0)
