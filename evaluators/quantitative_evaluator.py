from algorithms.algorithm_wrappers import *
from utils import *

import random
import itertools
import torch.optim as optim
import torch
import time
import scipy

## Evaluates performance of algorithm on small graphs by comparing numerical quality
## of algorithms with the brute-forced best solution and qualitative lower bound based
## on curvature of problem setting.
def quantitative_eval(graph_list, save_results = False):
    print("Input graphs found: " + str(len(graph_list)))
    test_results = []
    test_results_by_hops = []

    time_exact = 0
    time_iterative = 0
    time_quadratic = 0
    time_greedy = 0
    
    greedy_percents_list = []
    lower_bounds_by_hops_list = []

    best_solution_outside_egonet = 0
    disconnected_best_solution = 0
    
    avg_lower_bound = 0
    avg_lower_bound_hops = 0
    
    percentage_greedy_optimal_solution = 0
    percentage_iterative_optimal_solution = 0
    percentage_quadratic_optimal_solution = 0
    
    percentage_greedy_best_solution = 0

    count = 0
    for items in graph_list:
        count += 1
        print("Processing graph " + str(count) + "/" + str(len(graph_list)))

        G = items[0]
        L = items[1]
        W = items[2]
        current_team = items[3]
        to_replace = items[4]

        A = nx.adjacency_matrix(G)

        ## restart probability; set to 1 / (10 * graph_size)
        c = 1 / (10 * A.shape[0])

        remaining_team = diff(current_team, to_replace)

        ## compute candidates (nodes within |to_replace| hops from members in remaining_team)
        possible_candidates = get_possible_candidates(G, remaining_team, to_replace)

        ## compute curvature to obtain bound of solution
        curvature = kernel_curvature(A, L, W, c, current_team, to_replace)
        curvature_by_hops = kernel_curvature(A, L, W, c, current_team, to_replace, possible_candidates)

        ## brute-forced best solution. Combined with curvature to plot worst case performance line.
        temp_time = time.time()
        team_exact, team_exact_by_hops = replace_subteam_brute_force(G, A, L, W, c, current_team, to_replace, possible_candidates)
        temp_time_exact = (time.time() - temp_time)

        if not nx.is_connected(G.subgraph(team_exact)):
            if team_exact != team_exact_by_hops:
                best_solution_outside_egonet += 1
            disconnected_best_solution += 1

        ## baselines.
        temp_time = time.time()
        team_iterative = replace_subteam_iterative(A, L, W, c, current_team, to_replace)
        temp_time_iterative = (time.time() - temp_time)
        temp_time = time.time()
        team_quadratic = replace_subteam_quadratic(A, L, W, c, current_team, to_replace)
        temp_time_quadratic = (time.time() - temp_time)

        ## subteam-rep-fast-exact.
        temp_time = time.time()
        team_greedy = replace_subteam_greedy(A, L, W, c, current_team, to_replace)
        temp_time_greedy = (time.time() - temp_time)


        ## if any algorithm fails to return a new team (which happens if replaced members form bridge(s) between remaining team and rest of graph)
        if not team_exact or not team_exact_by_hops or not team_iterative or not team_quadratic or not team_greedy:
            print("Team in graph " + str(count) + "/" + str(len(graph_list)) + " does not contain valid structure for replacement.")
            continue

        time_exact += temp_time_exact
        time_iterative += temp_time_iterative
        time_quadratic += temp_time_quadratic
        time_greedy += temp_time_greedy

        ## kernel values of solutions returned by algorithms.
        base_val = svn_kernel_argmax(A, L, W, c, current_team, remaining_team, sum = True)
        exact_val = svn_kernel_argmax(A, L, W, c, current_team, team_exact, sum = True)
        exact_val_by_hops = svn_kernel_argmax(A, L, W, c, current_team, team_exact_by_hops, sum = True)

        iterative_val = svn_kernel_argmax(A, L, W, c, current_team, team_iterative, sum = True)
        quadratic_val = svn_kernel_argmax(A, L, W, c, current_team, team_quadratic, sum = True)
        greedy_val = svn_kernel_argmax(A, L, W, c, current_team, team_greedy, sum = True)

        lower_bound = 1 - curvature
        lower_bound_by_hops = 1 - curvature_by_hops

        iterative_percent = (iterative_val - base_val) / (exact_val - base_val)
        quadratic_percent = (quadratic_val - base_val) / (exact_val - base_val)
        greedy_percent = (greedy_val - base_val) / (exact_val - base_val)

        iterative_percent_by_hops = (iterative_val - base_val) / (exact_val_by_hops - base_val)
        quadratic_percent_by_hops = (quadratic_val - base_val) / (exact_val_by_hops - base_val)
        greedy_percent_by_hops = (greedy_val - base_val) / (exact_val_by_hops - base_val)

        test_results.append((lower_bound, iterative_percent, quadratic_percent, greedy_percent))
        test_results_by_hops.append((lower_bound_by_hops, iterative_percent_by_hops, quadratic_percent_by_hops, greedy_percent_by_hops))
        
        if iterative_val >= exact_val:
            percentage_iterative_optimal_solution += 1
        if quadratic_val >= exact_val:
            percentage_quadratic_optimal_solution += 1
        if greedy_val >= exact_val:
            percentage_greedy_optimal_solution += 1
            
        if greedy_val >= iterative_val and greedy_val >= quadratic_val:
            percentage_greedy_best_solution += 1
            
        greedy_percents_list.append(greedy_percent_by_hops)
        lower_bounds_by_hops_list.append(lower_bound_by_hops)
        
        avg_lower_bound += lower_bound
        avg_lower_bound_hops += lower_bound_by_hops

    print("average time exact: " + str(time_exact / len(graph_list)))
    print("average time iterative: " + str(time_iterative / len(graph_list)))
    print("average time quadratic: " + str(time_quadratic / len(graph_list)))
    print("average time greedy: " + str(time_greedy / len(graph_list)))
    print("percentage graphs with best solution outside |P|-hop egonet: " + str(best_solution_outside_egonet / len(graph_list)))
    print("percentage graphs with disconnected_best_solution: " + str(disconnected_best_solution / len(graph_list)))
    print("Average lower bound of entire graph: " + str(avg_lower_bound / len(graph_list)))
    print("Average lower bound of egonet: " + str(avg_lower_bound_hops / len(graph_list)))
    print("Evaluated " + str(len(test_results)) + "/" + str(len(graph_list)) + " graphs.")
    
    print("Percentage graphs where greedy algorithm finds optimal solution: " + str(percentage_greedy_optimal_solution / len(graph_list)))
    print("Percentage graphs where iterative algorithm finds optimal solution: " + str(percentage_iterative_optimal_solution / len(graph_list)))
    print("Percentage graphs where quadratic algorithm finds optimal solution: " + str(percentage_quadratic_optimal_solution / len(graph_list)))
    
    print("Percentage graphs where greedy algorithm outperforms baselines: " + str(percentage_greedy_best_solution / len(graph_list)))
    
    print("Correlation coefficient between greedy solution quality and lower bound: " + str(np.corrcoef(np.array(greedy_percents_list), np.array(lower_bounds_by_hops_list))[0][1]))

    return(test_results, test_results_by_hops, time_exact / len(graph_list), time_iterative / len(graph_list), time_quadratic / len(graph_list), time_greedy / len(graph_list), best_solution_outside_egonet / len(graph_list), disconnected_best_solution / len(graph_list), avg_lower_bound / len(graph_list), avg_lower_bound_hops / len(graph_list), percentage_greedy_optimal_solution / len(graph_list), percentage_iterative_optimal_solution / len(graph_list), percentage_quadratic_optimal_solution / len(graph_list), percentage_greedy_best_solution / len(graph_list), np.corrcoef(np.array(greedy_percents_list), np.array(lower_bounds_by_hops_list))[0][1])
