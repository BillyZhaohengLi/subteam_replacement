from algorithms.find_person import *

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

diff = lambda l1,l2: [x for x in l1 if x not in l2]

## Replaces all members simultaneously in to_replace of current_team
## A: unnormalized adjacency matrix
## L: skill matrix
## W: skill adjacency matrix
## c: restart probability
def replace_subteam_greedy(A, L, W, c, current_team, to_replace):
    remaining_team = diff(current_team, to_replace)
    new_members = []

    while (len(remaining_team) < len(current_team)):
        person_and_score = find_best_person(A, L, W, c, current_team, remaining_team)

        ## happens if replaced team member forms a bridge between current team and rest of graph
        if person_and_score == None:
            return None
        remaining_team.append(person_and_score[0])
        new_members.append(person_and_score[0])
    return new_members
