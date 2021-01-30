from algorithms.teamrep_fast_exact_node_labeled import *
from algorithms.teamrep_fast_exact_edge_labeled import *
from algorithms.edge_labeled_kernel import *

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

    while (len(remaining_team) < len(current_team)):
        person_and_score = teamrep_fast_exact_edge_labeled_argmax(A, L, W, c, current_team, remaining_team)

        ## happens if replaced team member forms a bridge between current team and rest of graph
        if person_and_score == None:
            return None
        remaining_team.append(person_and_score[0])
    return remaining_team

## Iteratively replace team members in order given by to_replace array
def replace_subteam_iterative(A, L, W, c, current_team, to_replace):
    remaining_team = copy.deepcopy(current_team)

    for person in to_replace:
        try:
            remaining_team.remove(person)
        except:
            print("person " + str(person) + " not in original team")
            return None

        person_and_score = teamrep_fast_exact_edge_labeled_argmax(A, L, W, c, current_team, remaining_team)

        ## happens if replaced team member forms a bridge between current team and rest of graph
        if person_and_score == None:
            return None
        remaining_team.append(person_and_score[0])
    return remaining_team

## Iteratively replace team members, at each step replacing team member that results in largest increase (or smallest decrease) in kernel value.
## Hence this function scales quadratically with num_to_replace.
def replace_subteam_quadratic(A, L, W, c, current_team, to_replace):
    remaining_team = copy.deepcopy(current_team)
    to_replace_copy = copy.deepcopy(to_replace)

    while to_replace_copy:
        best_person = None
        best_person_to_replace = None
        best_score = float("-inf")

        for person in to_replace_copy:
            remaining_team_copy = copy.deepcopy(remaining_team)
            try:
                remaining_team_copy.remove(person)
            except:
                print("person " + str(person) + " not in original team")
                return None

            person_and_score = teamrep_fast_exact_edge_labeled_argmax(A, L, W, c, current_team, remaining_team_copy)

            if person_and_score != None and person_and_score[1] > best_score:
                best_person = person_and_score[0]
                best_person_to_replace = person
                best_score = person_and_score[1]

        if best_person == None:
            return None
        remaining_team.remove(best_person_to_replace)
        to_replace_copy.remove(best_person_to_replace)
        remaining_team.append(best_person)

    return remaining_team

## Brute forces all combinations to find best replacement subteam.
## will timeout with larger graphs and/or larger number of members to replace.
def replace_subteam_brute_force(G, A, L, W, c, current_team, to_replace, possible_candidates = None):

    remaining_team = diff(current_team, to_replace)
    num_to_replace = len(to_replace)

    candidates = diff(list(range(A.shape[1])), current_team)

    viable_combinations = [c for c in combinations(candidates, num_to_replace)]

    max_combination = None
    max_kernel = float("-inf")

    max_combination_by_hops = None
    max_kernel_by_hops = float("-inf")

    for combination in viable_combinations:
        if len(diff(list(nx.isolates(G.subgraph(remaining_team + list(combination)))), remaining_team)):
            continue
            
        val = edge_labeled_kernel_argmax(A, L, W, c, current_team, remaining_team + list(combination))
        if val > max_kernel:
            max_combination = combination
            max_kernel = val
        if set(combination).issubset(set(possible_candidates)) and val > max_kernel_by_hops:
            max_combination_by_hops = combination
            max_kernel_by_hops = val

    ## happens if replaced team member forms a bridge between current team and rest of graph
    max_list = None
    max_list_by_hops = None

    if max_combination:
        max_list = remaining_team + list(max_combination)
    if max_combination_by_hops:
        max_list_by_hops = remaining_team + list(max_combination_by_hops)

    if possible_candidates == None:
        return max_list
    return max_list, max_list_by_hops

## Computes the curvature of a given problem setting.
## The curvature indicates the lower bound of the numerical quality of
## a solution returned by the greedy algorithm.
def kernel_curvature(A, L, W, c, current_team, to_replace, possible_candidates = None):
    remaining_team = diff(current_team, to_replace)

    ## kernel of remaining team with original team
    base_val = edge_labeled_kernel_argmax(A, L, W, c, current_team, remaining_team, sum = True)

    candidates = None
    if possible_candidates:
        ## use precomputed candidates within |to_replace| hops if applicable
        candidates = possible_candidates
    else:
        ## candidates as all nodes not in current_team
        candidates = diff(list(range(A.shape[1])), current_team)

    ## kernel of (remaining team + all candidates) with original team
    greatest_val = edge_labeled_kernel_argmax(A, L, W, c, current_team, remaining_team + candidates, sum = True)

    curvature = float("-inf")
    for person in candidates:
        ## kernel of (remaining team + new candidate) with original team
        cand_val = edge_labeled_kernel_argmax(A, L, W, c, current_team, remaining_team + [person], sum = True)

        ## kernel of (remaining team + all other candidates) with original team
        others_val = edge_labeled_kernel_argmax(A, L, W, c, current_team, diff(remaining_team + candidates, [person]), sum = True)

        curvature_value = 1 - (cand_val - base_val) / (greatest_val - others_val)
        if curvature_value > curvature:
            curvature = curvature_value

    return curvature
