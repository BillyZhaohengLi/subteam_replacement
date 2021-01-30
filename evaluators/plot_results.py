from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
import statsmodels.api as sm
import pickle
import sys
import numpy as np

def plot_results_bound(test_results, parameters):
    ## sort results in descending value of curvature
    test_results.sort(reverse = True)

    test_results_lists = list(map(list, zip(*test_results)))
    curvature_values = test_results_lists[0]
    iterative_percentages = test_results_lists[1]
    quadratic_percentages = test_results_lists[2]
    greedy_percentages = test_results_lists[3]
    
    graph_size = parameters[0]
    team_size = parameters[1]
    number_replaced = parameters[2]
    egonet_only = parameters[3]

    plt.plot(np.arange(len(curvature_values)), np.array(curvature_values), label = '1-curvature', linestyle = '--', color = 'darkblue')
    plt.plot(np.arange(len(greedy_percentages)), np.array(greedy_percentages), label = 'REFORM', color = 'crimson')
    plt.xlabel("Experiment no. ordered by decreasing lower bound")
    plt.ylabel("Proportion of optimal solution")
    plt.title("Greedy solution quality and lower bound, |G|=" + str(graph_size) + ",|T|=" + str(team_size) + ",|P|=" + str(number_replaced) + ",egonet=" + str(egonet_only))

    plt.ylim(0.3, 1.05)
    plt.legend(loc='best')
    
    plt.savefig('figures/BA/bounds_G' + str(graph_size) + 'T' + str(team_size) + 'P' + str(number_replaced) + "egonet" + str(egonet_only) + '.png')
    plt.clf()

    plt.plot(np.arange(len(iterative_percentages)), np.array(iterative_percentages), label = 'Iterative', linestyle = ":")
    plt.plot(np.arange(len(quadratic_percentages)), np.array(quadratic_percentages), label = 'Quadratic', linestyle = "-.")
    plt.plot(np.arange(len(greedy_percentages)), np.array(greedy_percentages), label = 'Ours', linestyle = '-', color = 'crimson')

    plt.ylim(0.9, 1.02)
    plt.legend(loc='best')
    plt.xlabel("Experiment no. ordered by decreasing lower bound")
    plt.ylabel("Proportion of optimal solution")
    plt.title("Greedy solution vs. baseline solutions, |G|=" + str(graph_size) + ",|T|=" + str(team_size) + ",|P|=" + str(number_replaced) + ",egonet=" + str(egonet_only))

    plt.savefig('figures/BA/performance_G' + str(graph_size) + 'T' + str(team_size) + 'P' + str(number_replaced) + "egonet" + str(egonet_only) + '.png')
    plt.clf()

def plot_results_large(test_results_score, test_results_time, parameters):

    test_results_score_lists = list(map(list, zip(*test_results_score)))
    greedy_values = test_results_score_lists[0]
    iterative_values = test_results_score_lists[1]
    quadratic_values = test_results_score_lists[2]
    
    test_results_time_lists = list(map(list, zip(*test_results_time)))
    greedy_time = test_results_time_lists[0]
    iterative_time = test_results_time_lists[1]
    quadratic_time = test_results_time_lists[2]
    
    team_size = parameters[0]
    number_replaced = parameters[1]
    iteration = parameters[2]
    
    width = 0.25

    plt.bar(np.arange(len(greedy_values)), np.array(greedy_values) / np.array(greedy_values), width, label = 'Ours', color = "crimson")
    plt.bar(np.arange(len(iterative_values)) + width, np.array(iterative_values) / np.array(greedy_values), width, label = 'Iterative', color = "darkblue")
    plt.bar(np.arange(len(quadratic_values)) + 2 * width, np.array(quadratic_values) / np.array(greedy_values), width, label = 'Quadratic', color = "green")
    plt.legend(loc='best')
    plt.xlabel("Experiment no.")
    plt.ylabel("Log proportion of greedy solution")
    plt.yscale("log")
    plt.title("Quality of baseline solutions vs. greedy solutions for |T|=" + str(team_size) + ",|P|=" + str(number_replaced))
    plt.savefig('figures/full_dblp/performance_T' + str(team_size) + 'P' + str(number_replaced) + "set" + str(number_replaced) + '.png')
    print("plotted figure")
    plt.show()
    plt.clf()
    
    plt.bar(np.arange(len(greedy_time)), np.array(greedy_time), width, label = 'Ours', color = "crimson")
    plt.bar(np.arange(len(iterative_time)) + width, np.array(iterative_time), width, label = 'Iterative', color = "darkblue")
    plt.bar(np.arange(len(quadratic_time)) + 2 * width, np.array(quadratic_time), width, label = 'Quadratic', color = "green")
    plt.legend(loc='best')
    plt.xlabel("Experiment no.")
    plt.ylabel("Log seconds to obtain solution")
    plt.yscale("log")
    plt.title("Time taken to obtain solution for |T|=" + str(team_size) + ",|P|=" + str(number_replaced))
    plt.savefig('figures/full_dblp/time_T' + str(team_size) + 'P' + str(number_replaced) + "set" + str(number_replaced) + '.png')
    print("plotted figure")
    plt.show()
    plt.clf()
    
def plot_results_properties(properties, graph_size):
    test_results_lists = list(map(list, zip(*properties)))
    team_size = test_results_lists[0]
    number_to_replace = test_results_lists[1]
    best_solution_outside_egonet = test_results_lists[2]
    disconnected_best_solution = test_results_lists[3]
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    #plt.title("Proportion of graphs with disconnected optimal solutions vs. |T| and |P|")
    
    ax.set_xlabel('|T|')
    ax.set_ylabel('|P|')
    ax.set_zlabel('Proportion')

    ax.set_xticks(list(range(3, 10)))
    ax.set_yticks(list(range(2, 5)))
 
    #ax.scatter(team_size, number_to_replace, best_solution_outside_egonet, marker = 'o', label = 'Optimal solution contains nodes outside |P|-egonet of remaining team')
    ax.scatter(team_size, number_to_replace, disconnected_best_solution, marker = 'p', label = 'Disconnected optimal solution')

    for x, y, z in zip(team_size, number_to_replace, disconnected_best_solution):
        ax.plot3D([x, x], [y, y], [z, 0], color = 'black', alpha = 0.2)

    ax.plot3D([2, 6], [1, 5], [0, 0], color = 'blue', label = '|P| = |T| - 1', alpha = 0.4)

    ax.legend(loc = 'lower left', borderaxespad = -4)

    ax.view_init(elev = 10, azim = -20)
    
    plt.savefig('figures/BA/propertiesG' + str(graph_size) + '.png')
    plt.show()
    plt.clf()
    
def plot_results_curvature(curvature, graph_size):
    test_results_lists = list(map(list, zip(*curvature)))
    team_size = test_results_lists[0]
    number_to_replace = test_results_lists[1]
    bounds = test_results_lists[2]
    bounds_by_hops = test_results_lists[3]
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    #plt.title("Avg. lower bound of quality of solution from greedy alg'm vs. |T|, |P|")
    
    ax.set_xlabel('|T|')
    ax.set_ylabel('|P|')
    ax.set_zlabel('Avg. lower bound (1 - curvature)')

    ax.set_xticks(list(range(3, 10)))
    ax.set_yticks(list(range(2, 5)))
    
    ax.scatter(team_size, number_to_replace, bounds, marker = 'o', label = 'Lower bound')
    #ax.scatter(team_size, number_to_replace, bounds_by_hops, marker = 'p', label = 'Lower bound computed with |P|-egonet of remaining team')

    #ax.legend(loc = 'lower left', borderaxespad = -4)

    for x, y, z in zip(team_size, number_to_replace, bounds):
        ax.plot3D([x, x], [y, y], [z, 0.92], color = 'black', alpha = 0.2)

    ax.view_init(elev = 10, azim = -20)
    
    plt.savefig('figures/BA/curvatureG' + str(graph_size)  + '.png')
    plt.show()
    plt.clf()
    
def plot_results_times(times, graph_size):
    print(times)

    for i in range(5, 10):
        g2 = 0
        g3 = 0
        g4 = 0
        i2 = 0
        i3 = 0
        i4 = 0
        q2 = 0
        q3 = 0
        q4 = 0
        for t in times:
            if (t[0] == i and t[1] == 2):
                g2 = t[5]
                i2 = t[3]
                q2 = t[4]
            if (t[0] == i and t[1] == 3):
                g3 = t[5]
                i3 = t[3]
                q3 = t[4]
            if (t[0] == i and t[1] == 4):
                g4 = t[5]
                i4 = t[3]
                q4 = t[4]
        print(g4 - g3, g3 - g2)
        print(i4 - i3, i3 - i2)
        print(q4 - q3, q3 - q2)
        print("---------")
   
    
    test_results_lists = list(map(list, zip(*times)))
    team_size = test_results_lists[0]
    number_to_replace = test_results_lists[1]
    time_exact = test_results_lists[2]
    time_iterative = test_results_lists[3]
    time_quadratic = test_results_lists[4]
    time_greedy = test_results_lists[5]
    

    fig = plt.figure()
    
    ax = fig.add_subplot(111, projection='3d')
    ax.tick_params(labelsize = 15)
    
    #plt.title("Average time to find solution vs. |T| and |P|")
    
    ax.set_xlabel('Team size',fontsize = 15, labelpad = 5)
    ax.set_ylabel('Size of replaced subteam',fontsize = 15, labelpad = 10)
    ax.set_zlabel('Average time to find solution (seconds)',fontsize = 15, labelpad = 5)

    ax.set_xticks(list(range(3, 10)))
    ax.set_yticks(list(range(2, 5)))

    for x, y, z in zip(team_size, number_to_replace, time_quadratic):
        ax.plot3D([x, x], [y, y], [z, 0], color = 'black', alpha = 0.2, linestyle = ':')
    
    #ax.scatter(team_size, number_to_replace, time_exact, marker = 'o')
    ax.scatter(team_size, number_to_replace, time_quadratic, label = 'LocalBest', marker = 's', s = 60, depthshade = False)
    ax.scatter(team_size, number_to_replace, time_iterative, label = 'Iterative',marker = 'P', s = 60, depthshade = False)
    ax.scatter(team_size, number_to_replace, time_greedy, label = 'REFORM', marker = '*', s = 60, depthshade = False)
    
    ax.legend(loc = 'upper left',borderaxespad = 6,fontsize = 15)

    ax.view_init(elev = 10, azim = -20)

    plt.subplots_adjust(left = -0.1, bottom = 0, right = 1, top = 1.1)
    plt.savefig('figures/BA/timesG' + str(graph_size)  + '.png')
    plt.show()
    plt.clf()
    
def plot_results_optimal_solutions(stats, graph_size):
    test_results_lists = list(map(list, zip(*stats)))
    team_size = test_results_lists[0]
    number_to_replace = test_results_lists[1]
    percentage_greedy_optimal_solution = test_results_lists[2]
    percentage_iterative_optimal_solution = test_results_lists[3]
    percentage_quadratic_optimal_solution = test_results_lists[4]

    for i in range(len(percentage_greedy_optimal_solution)):
        percentage_greedy_optimal_solution[i] *= 100
    for i in range(len(percentage_iterative_optimal_solution)):
        percentage_iterative_optimal_solution[i] *= 100
    for i in range(len(percentage_quadratic_optimal_solution)):
        percentage_quadratic_optimal_solution[i] *= 100
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.tick_params(labelsize = 15)

    #plt.title("Proportion of graphs where algorithms finds optimal solution vs. |T| and |P|")
    
    ax.set_xlabel('Team size',fontsize = 15, labelpad = 5)
    ax.set_ylabel('Size of replaced subteam',fontsize = 15, labelpad = 10)
    ax.set_zlabel('% of graphs finding optimal solution',fontsize = 15, labelpad = 5)

    ax.set_xticks(list(range(3, 10)))
    ax.set_yticks(list(range(2, 5)))
    
    #ax.scatter(team_size, number_to_replace, time_exact, marker = 'o')
    ax.scatter(team_size, number_to_replace, percentage_quadratic_optimal_solution, label = 'LocalBest', marker = 's', s = 60, depthshade = False, zorder = 10)
    ax.scatter(team_size, number_to_replace, percentage_iterative_optimal_solution, label = 'Iterative',marker = 'P', s = 60, depthshade = False, zorder = 5)
    ax.scatter(team_size, number_to_replace, percentage_greedy_optimal_solution, label = 'REFORM', marker = '*', s = 60, depthshade = False, zorder = 0)
    ax.legend(loc = 'upper right',borderaxespad = 4,fontsize = 15)

    for x, y, z in zip(team_size, number_to_replace, list(map(max, zip(percentage_greedy_optimal_solution, percentage_iterative_optimal_solution, percentage_quadratic_optimal_solution)))):
        ax.plot3D([x, x], [y, y], [z, 0], color = 'black', alpha = 0.2)

    ax.view_init(elev = 10, azim = -20)
    
    plt.subplots_adjust(left = -0.1, bottom = 0, right = 1, top = 1.1)
    plt.savefig('figures/BA/optimalsolutionG' + str(graph_size) + '.png')
    plt.show()
    plt.clf()
    
def plot_results_best_solutions(stats, graph_size):
    test_results_lists = list(map(list, zip(*stats)))
    team_size = test_results_lists[0]
    number_to_replace = test_results_lists[1]
    percentage_greedy_best_solution = test_results_lists[2]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    #plt.title("Proportion of graphs with greedy alg'm outperforming baselines vs. |T|, |P|")
    
    ax.set_xlabel('Team size',fontsize = 12)
    ax.set_ylabel('Size of replaced subteam',fontsize = 12)
    ax.set_zlabel('Proportion of graphs REFORM outperforms baselines',fontsize = 12)

    #ax.set_xlabel('Team size')
    #ax.set_ylabel('Size of replaced subteam')
    #ax.set_zlabel('Proportion of graphs REFORM outperforms baselines')

    ax.set_xticks(list(range(3, 10)))
    ax.set_yticks(list(range(2, 5)))

    for x, y, z in zip(team_size, number_to_replace, percentage_greedy_best_solution):
        ax.plot3D([x, x], [y, y], [z, 0.4], color = 'black', alpha = 0.2)

    ax.scatter(team_size, number_to_replace, percentage_greedy_best_solution, marker = 'p')

    ax.view_init(elev = 10, azim = -20)
    
    plt.subplots_adjust(left = -0.1, bottom = 0, right = 1, top = 1.1)
    plt.savefig('figures/BA/bestsolutionG' + str(graph_size)  + '.png')
    plt.show()
    plt.clf()
    
def plot_results_brute_force(stats, graph_size):
    print(stats)
    test_results_lists = list(map(list, zip(*stats)))
    team_size = test_results_lists[0]
    number_to_replace = test_results_lists[1]
    solution_times_exact = test_results_lists[2]
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    #plt.title("Average time to brute force solution vs. |T| and |P|")
    
    ax.set_xlabel('|T|')
    ax.set_ylabel('|P|')
    ax.set_zlabel('Average time (seconds)')

    ax.set_xticks(list(range(3, 10)))
    ax.set_yticks(list(range(2, 5)))
    ax.set_zlim3d(0, 200)

    for y in range(2, 5):
        team_size_list = []
        solution_times_exact_list = []
        for i in range(len(number_to_replace)):
            if number_to_replace[i] == y:
                team_size_list.append(team_size[i])
                solution_times_exact_list.append(solution_times_exact[i])

        X = sm.add_constant(np.array(team_size_list))

        model = sm.OLS(np.array(solution_times_exact_list), X)
        result = model.fit()
        intercept = result.params[0]
        slope = result.params[1]
        
        x = np.linspace(y, 10)
        
        ax.plot(x, np.zeros(50) + y, intercept + x * slope, color = 'blue', alpha = 0.4)

    for x in range(5, 10):
        number_to_replace_list = []
        solution_times_exact_list = []
        for i in range(len(team_size)):
            if team_size[i] == x:
                number_to_replace_list.append(number_to_replace[i])
                solution_times_exact_list.append(solution_times_exact[i])

        result = np.polyfit(np.array(number_to_replace_list), np.log(np.array(solution_times_exact_list)), 1, w =  np.sqrt(np.array(solution_times_exact_list)))
        intercept = result[1]
        slope = result[0]

        
        y = np.linspace(1, 5)
        
        ax.plot(np.zeros(50) + x, y, np.exp(intercept + y * slope), color = 'green', alpha = 0.4)
        
    
    #ax.zaxis.set_scale('log')
    
    ax.scatter(team_size, number_to_replace, solution_times_exact, marker = '*', color = 'black')

    ax.view_init(elev = 10, azim = -80)
    
    plt.savefig('figures/BA/bruteforceG' + str(graph_size)  + '.png')
    plt.show()
    plt.clf()
    
def plot_results_corrcoef(stats, graph_size):
    test_results_lists = list(map(list, zip(*stats)))
    team_size = test_results_lists[0]
    number_to_replace = test_results_lists[1]
    quality_corrcoef = test_results_lists[2]

    #normal = np.array([0, 0, 1])
    #d = 0
    #xx, yy = np.meshgrid(range(10), range(10))
    #z = (-normal[0] * xx - normal[1] * yy - d) * 1. / normal[2]
    
    fig = plt.figure().gca(projection='3d')
    ax = plt.axes(projection='3d')
    
    ax.set_xlabel('|T|')
    ax.set_ylabel('|P|')
    ax.set_zlabel('Correlation coefficient')

    ax.set_xticks(list(range(3, 10)))
    ax.set_yticks(list(range(2, 5)))
    
    ax.scatter3D(team_size, number_to_replace, quality_corrcoef, marker = '*', color = 'black')

    #plt.title("Correlation between solution quality & lower bound vs. |T| and |P|")

    for x, y, z in zip(team_size, number_to_replace, quality_corrcoef):
        ax.plot3D([x, x], [y, y], [z, 0], color = 'blue')


    #ax.plot3D([3, 9], [2, 2], [0, 0], color = 'blue', alpha = 0.2)
    #ax.plot3D([4, 9], [3, 3], [0, 0], color = 'blue', alpha = 0.2)
    #ax.plot3D([5, 9], [4, 4], [0, 0], color = 'blue', alpha = 0.2)

    #ax.plot3D([4, 4], [2, 3], [0, 0], color = 'blue', alpha = 0.2)
    #ax.plot3D([5, 5], [2, 4], [0, 0], color = 'blue', alpha = 0.2)
    #ax.plot3D([6, 6], [2, 4], [0, 0], color = 'blue', alpha = 0.2)
    #ax.plot3D([7, 7], [2, 4], [0, 0], color = 'blue', alpha = 0.2)
    #ax.plot3D([8, 8], [2, 4], [0, 0], color = 'blue', alpha = 0.2)
    #ax.plot3D([9, 9], [2, 4], [0, 0], color = 'blue', alpha = 0.2)

    #ax.plot3D([3, 5], [2, 4], [0, 0], color = 'blue', alpha = 0.2)

    ax.view_init(elev = 10, azim = -20)

    plt.savefig('figures/BA/corrcoefG' + str(graph_size)  + '.png')
    plt.show()
    plt.clf()

# # run file directory to plot already computed results.
# test_results = None
# try:
#    test_results = pickle.load(open("results/test_results.pickle", "rb"))
# except:
#    print("Results do not exist!")
#    sys.exit(1)
# plot_results(test_results)
