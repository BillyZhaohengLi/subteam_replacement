from tkinter import *
from tkinter import ttk
import tkinter as tk
from ScrollableFrame import ScrollableFrame
from ScrollableFrame import DoubleScrollableFrame
from algorithms.greedy import replace_subteam_greedy

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

import networkx as nx

import scipy.io as sio
import numpy as np
import scipy.sparse
import time
import copy
import pickle

## dataset items----------------------------------------------------------
global dataset
global adj
global L

global num_to_author
global author_to_num
global author_list
global conference_to_num
global num_to_conference

global previous_author_id
global current_author_id

## Hyperparameters
global W

## Team manager items
global remaining_team
global to_replace
global replacements_found

## Visualization graph
global visualization_graph
global canvas
global fig
global ax

global draw_remaining
global draw_to_replace
global draw_results

## dataset setup----------------------------------------------------------
## authors
file1 = open('data/authorDict.txt', 'r')
num_to_author = dict()
author_to_num = dict()
author_list = []
Lines = file1.readlines()
i = 0
for line in Lines:
	author_name = line.rstrip()
	author_to_num[author_name] = i
	num_to_author[i] = author_name
	author_list.append(author_name)
	i += 1
author_list.sort()

## conferences
file1 = open('data/conferences.txt', 'r')
num_to_conference = dict()
conference_to_num = dict()
Lines = file1.readlines()
i = 0
for line in Lines:
	conference_to_num[line.rstrip()] = i
	num_to_conference[i] = line.rstrip()
	i += 1

## graph 
dataset = sio.loadmat('data/DBLP.mat')
adj = dataset['aa']
adj.setdiag(0)
L = dataset['count_label']
L = np.asarray(L.todense())

W = np.ones((L.shape[1], L.shape[1]))

## lists
remaining_team = dict()
to_replace = dict()
replacements_found = dict()

previous_author_id = None
current_author_id = None

## graph
visualization_graph = nx.Graph()

## interface setup-------------------------------------------

master = Tk()
master.title('Subteam Replacement Demo')

tabs = ttk.Notebook(master, width = 100, height = 600)

search_tab = ttk.Frame(tabs)
node_tab = ttk.Frame(tabs)
team_tab = ttk.Frame(tabs)
parameter_tab = ttk.Frame(tabs)

tabs.add(search_tab, text ='Search')
tabs.add(node_tab, text ='Node info')
tabs.add(team_tab, text ='Team manager')
tabs.add(parameter_tab, text ='Hyperparameters')

tabs.grid(row = 0, column = 3)

## plot & visualization setup---------------------------------	
## options

fig = Figure(figsize=(6.3, 6.3), dpi=100)

canvas = FigureCanvasTkAgg(fig, master=master)  # A tk.DrawingArea.
canvas.draw()

ax = fig.add_subplot(111, projection='3d')
ax._axis3don = False

canvas.get_tk_widget().grid(row = 0, column = 0, columnspan = 3)

def remaining_team_random():
	return (np.random.uniform(-0.5, 1), np.random.uniform(-0.5, 1), np.random.uniform(-0.5, 1))

def to_replace_random():
	return (np.random.uniform(-1, -0.5), np.random.uniform(-0.5, 1), np.random.uniform(-0.5, 1))

def results_random():
	return (np.random.uniform(-0.5, 1), np.random.uniform(-1, -0.5), np.random.uniform(-0.5, 1))

def plot_points(team, colorcenter, colorborder):
	for person in team.keys():
		publications = np.sum(L[person])
		ax.text(*team[person], num_to_author[person], size = 10)
		ax.scatter(*team[person], c = [colorcenter], s = [publications], edgecolors = colorborder)

def plot_edges(team1, team2, color, alpha, style):
	for person1 in team1.keys():
		for person2 in team2.keys():
			strength = adj[person1, person2]
			if strength > 0:
				ax.plot3D([team1[person1][0], team2[person2][0]], [team1[person1][1], team2[person2][1]], [team1[person1][2], team2[person2][2]], color = color, alpha = alpha, linestyle = style, linewidth = np.sqrt(strength))

def update_plot():
	ax.clear()

	if draw_remaining.get() == 1:
		plot_points(remaining_team, 'lime', 'green')
		plot_edges(remaining_team, remaining_team, 'green', 0.5, 'solid')

	if draw_to_replace.get() == 1:
		plot_points(to_replace, 'orangered', 'red')
		plot_edges(to_replace, to_replace, 'red', 0.5, 'solid')

	if draw_results.get() == 1:
		plot_points(replacements_found, 'goldenrod', 'gold')
		plot_edges(replacements_found, replacements_found, 'gold', 0.5, 'solid')

	if draw_remaining.get() == 1 and draw_to_replace.get() == 1:
		plot_edges(remaining_team, to_replace, 'red', 0.2, 'dotted')

	if draw_remaining.get() == 1 and draw_results.get() == 1:
		plot_edges(remaining_team, replacements_found, 'gold', 0.2, 'dotted')

	ax._axis3don = False
	fig.canvas.draw()

draw_remaining = IntVar(value = 1)
draw_remaining_button = Checkbutton(master, text = 'show remaining team members', variable = draw_remaining, command = update_plot)
draw_remaining_button.grid(row = 1, column = 0)

draw_to_replace = IntVar(value = 1)
draw_to_replace_button = Checkbutton(master, text = 'show team members to replace', variable = draw_to_replace, command = update_plot)
draw_to_replace_button.grid(row = 1, column = 1)

draw_results = IntVar(value = 1)
draw_results_button = Checkbutton(master, text = 'show replacements', variable = draw_results, command = update_plot)
draw_results_button.grid(row = 1, column = 2)

## Team manager tab-------------------------------------------
remaining_team_label = Label(team_tab, text = "Remaining team (S):")
remaining_team_label.pack()

remaining_team_frame = ScrollableFrame(team_tab, height = 180)
remaining_team_frame.pack()

to_replace_label = Label(team_tab, text = "Members to replace (R):")
to_replace_label.pack()

to_replace_frame = ScrollableFrame(team_tab, height = 180)
to_replace_frame.pack()

results_label = Label(team_tab, text = "Replacements found (S'):")
results_label.pack()

results_frame = ScrollableFrame(team_tab, height = 180)
results_frame.pack()

def add_to_list(name_id, team_dict1, team_dict2, location):
	if name_id not in team_dict1 and name_id not in team_dict2:
		team_dict1[name_id] = location
		refresh()
		update_plot()

def remove_from_list(name_id, team_dict):
	del team_dict[name_id]
	refresh()
	update_plot()

def remove_and_add(name_id, team_dict1, team_dict2, location):
	del team_dict1[name_id]
	team_dict2[name_id] = location
	refresh()
	update_plot()

def refresh():
	for item in remaining_team_frame.scrollable_frame.winfo_children():
		item.destroy()
	for item in to_replace_frame.scrollable_frame.winfo_children():
		item.destroy()
	for item in results_frame.scrollable_frame.winfo_children():
		item.destroy()

	for i in range(4):
		remaining_team_frame.columnconfigure(i, weight = 1)

	remaining_team_frame.scrollable_frame.columnconfigure(1, weight = 1)
	## add remaining team
	remain_row = 0
	for name_id in remaining_team.keys():
		name_label = Label(remaining_team_frame.scrollable_frame, text = num_to_author[name_id], anchor='w')
		name_label.grid(row=remain_row, column = 0)

		remove_func = lambda name_id=name_id, team_dict=remaining_team: remove_from_list(name_id, team_dict)
		remove_button = Button(remaining_team_frame.scrollable_frame, text = "Remove", command=remove_func)
		remove_button.grid(row=remain_row, column = 1, sticky = 'e')

		replace_func = lambda name_id=name_id, team_dict1=remaining_team, team_dict2 = to_replace: remove_and_add(name_id, team_dict1, team_dict2, to_replace_random())
		replace_button = Button(remaining_team_frame.scrollable_frame, text = "Replace", command=replace_func)
		replace_button.grid(row=remain_row, column = 2, sticky = 'e')

		select_func = lambda name_id=name_id: select_node(name_id)
		detail_button = Button(remaining_team_frame.scrollable_frame, text = "Info", command=select_func)
		detail_button.grid(row=remain_row, column = 3, sticky = 'e')

		remain_row += 1

	## add to replace
	to_replace_frame.scrollable_frame.columnconfigure(1, weight = 1)
	replace_row = 0
	for name_id in to_replace.keys():
		name_label = Label(to_replace_frame.scrollable_frame, text = num_to_author[name_id], anchor='w')
		name_label.grid(row=replace_row, column = 0)

		remove_func = lambda name_id=name_id, team_dict=to_replace: remove_from_list(name_id, team_dict)
		remove_button = Button(to_replace_frame.scrollable_frame, text = "Remove", command=remove_func)
		remove_button.grid(row=replace_row, column = 1, sticky='e')

		replace_func = lambda name_id=name_id, team_dict1=to_replace, team_dict2 = remaining_team: remove_and_add(name_id, team_dict1, team_dict2, remaining_team_random())
		replace_button = Button(to_replace_frame.scrollable_frame, text = "Keep", command=replace_func)
		replace_button.grid(row=replace_row, column = 2, sticky='e')

		select_func = lambda name_id=name_id: select_node(name_id)
		detail_button = Button(to_replace_frame.scrollable_frame, text = "Info", command=select_func)
		detail_button.grid(row=replace_row, column = 3, sticky='e')

		replace_row += 1

	## add results
	results_frame.scrollable_frame.columnconfigure(1, weight = 1)
	results_row = 0
	for name_id in replacements_found.keys():
		name_label = Label(results_frame.scrollable_frame, text = num_to_author[name_id], anchor='w')
		name_label.grid(row=results_row, column = 0, sticky='e')

		select_func = lambda name_id=name_id: select_node(name_id)
		detail_button = Button(results_frame.scrollable_frame, text = "Info", command=select_func, anchor='e')
		detail_button.grid(row=results_row, column = 1, sticky='e')

		results_row += 1
	
## Node Info tab-------------------------------------------
selected_author = StringVar()
selected_author.set("No author selected.")

author_title = ttk.Frame(node_tab)
author_title.columnconfigure(1, weight = 1)

back_func = lambda: select_node(previous_author_id)
back_button = Button(author_title, text = "Back", command=back_func)
back_button.grid(row = 0, column = 0, sticky = 'w')

author_name_label = Label(author_title, textvariable = selected_author)
author_name_label.grid(row = 0, column = 1)

add_func = lambda: add_to_list(author_to_num[selected_author.get()], remaining_team, to_replace, remaining_team_random())
name_button = Button(author_title, text = "Add", command = add_func)
name_button.grid(row = 0, column = 2, sticky = 'e')

author_title.pack(fill="both", expand=True)

def select_node(name_id):
	global previous_author_id
	global current_author_id
	previous_author_id = current_author_id
	current_author_id = name_id
	for item in skills_frame.scrollable_frame.winfo_children():
		item.destroy()
	for item in neighbors_frame.scrollable_frame.winfo_children():
		item.destroy()

	name = num_to_author[name_id]
	selected_author.set(name)
	node_id = author_to_num[name]

	## read skills
	node_skills_sorted = []
	for skill_id in range(L.shape[1]):
		if L[node_id, skill_id] > 0:
			node_skills_sorted.append((L[node_id, skill_id], num_to_conference[skill_id]))	
	node_skills_sorted.sort(reverse = True)

	node_neighbors = list(range(adj.shape[0]))
	node_neighbors = np.array(node_neighbors)[np.asarray((np.sum(adj[np.ix_(node_neighbors, [node_id])], axis = 1) > 0)).squeeze()]

	node_neighbors_sorted = []
	for neighbor in node_neighbors:
		node_neighbors_sorted.append((adj[node_id, neighbor], num_to_author[neighbor]))
	node_neighbors_sorted.sort(reverse = True)

	## add skills to frame
	skills_frame.scrollable_frame.columnconfigure(1, weight = 1)
	skill_row = 0
	max_skill_level = max(node_skills_sorted)[0]
	for pair in node_skills_sorted:
		skill_name_label = Label(skills_frame.scrollable_frame, text = pair[1], anchor='w')
		skill_name_label.grid(row=skill_row, column = 0)
		skill_bar = ttk.Progressbar(skills_frame.scrollable_frame, orient = tk.HORIZONTAL, length = 250, mode = 'determinate')
		skill_bar['value'] = 100 * int(pair[0]) / max_skill_level
		skill_bar.grid(row=skill_row, column = 1)
		skill_level_label = Label(skills_frame.scrollable_frame, text = int(pair[0]))
		skill_level_label.grid(row=skill_row, column = 2, sticky = 'e')
		skill_row += 1

	
	#add neighbors to frame
	neighbors_frame.scrollable_frame.columnconfigure(1, weight = 1)
	neighbor_row = 0
	for pair in node_neighbors_sorted:
		neighbor_name_label = Label(neighbors_frame.scrollable_frame, text = pair[1])
		neighbor_name_label.grid(row=neighbor_row, column = 0, sticky = tk.W)
		neighbor_weight_label = Label(neighbors_frame.scrollable_frame, text = int(pair[0]), justify = 'right')
		neighbor_weight_label.grid(row=neighbor_row, column = 1, sticky = 'e')

		select_func = lambda name_id=author_to_num[pair[1]]: select_node(name_id)
		detail_button = Button(neighbors_frame.scrollable_frame, text = "Info", command=select_func)
		detail_button.grid(row=neighbor_row, column = 2, sticky = 'e')

		add_func = lambda name_id=author_to_num[pair[1]], team_dict1=remaining_team, team_dict2 = to_replace: add_to_list(name_id, team_dict1, team_dict2, remaining_team_random())
		name_button = Button(neighbors_frame.scrollable_frame, text = "Add", command = add_func)
		name_button.grid(row=neighbor_row, column = 3, sticky = 'e')

		neighbor_row += 1

	tabs.select(node_tab)

skills_label = Label(node_tab, text = "Author publications:")
skills_label.pack()

skills_frame = ScrollableFrame(node_tab, width = 100, height = 200)
skills_frame.pack()

neighbors_label = Label(node_tab, text = "Coauthored papers:")
neighbors_label.pack()

neighbors_frame = ScrollableFrame(node_tab, width = 100, height = 360)
neighbors_frame.pack()

## author search tab---------------------------------------------
def search_author():
	for item in search_results_frame.scrollable_frame.winfo_children():
		item.destroy()
	
	query = search_query.get().lower()

	search_results_frame.scrollable_frame.columnconfigure(1, weight = 1)
	name_row = 0
	for name in author_list:
		if query in name.lower():
			name_label = Label(search_results_frame.scrollable_frame, text = name, anchor='w')
			name_label.grid(row=name_row, column = 0)

			select_func = lambda name_id=author_to_num[name]: select_node(name_id)
			detail_button = Button(search_results_frame.scrollable_frame, text = "Info", command=select_func)
			detail_button.grid(row=name_row, column = 1, sticky = 'e')

			add_func = lambda name_id=author_to_num[name], team_dict1=remaining_team, team_dict2 = to_replace: add_to_list(name_id, team_dict1, team_dict2, remaining_team_random())
			name_button = Button(search_results_frame.scrollable_frame, text = "Add", command=add_func)
			name_button.grid(row=name_row, column = 2, sticky = 'e')

			name_row += 1

search_query = Entry(search_tab, width = 50)
search_query.insert(END, 'Search for an author to begin:')
search_query.pack()

search_button = Button(search_tab, text = "Search", command = search_author)
search_button.pack()

search_results_frame = ScrollableFrame(search_tab)
search_results_frame.pack(fill = 'y', expand = 'True')

## Hyperparameters tab----------------------------------------
def set_W(matrix):
	W = matrix

W_label = Label(parameter_tab, text = "Skill adjacency matrix (W):")
W_label.pack()

W_presets = ttk.Frame(parameter_tab)
W_presets.columnconfigure(0, weight = 1)
W_presets.columnconfigure(1, weight = 1)

eye_func = lambda: set_W(np.eye(L.shape[1]))
eye_button = Button(W_presets, text = "np.eye", command=eye_func)
eye_button.grid(row = 0, column = 0)

ones_func = lambda: set_W(np.ones((L.shape[1], L.shape[1])))
ones_button = Button(W_presets, text = "np.ones", command=ones_func)
ones_button.grid(row = 0, column = 1)

W_presets.pack(fill="both")

c_label = Label(parameter_tab, text = "Restart probability (c):")
c_label.pack()

c_value = tk.Label(parameter_tab, text="0.000000000001")
c_value.pack()
c_scale = tk.Scale(parameter_tab, from_=-120, to=-40, tickinterval=0.1, orient="horizontal", showvalue=0, length = 300)
c_scale.config(command=lambda e: c_value.config(text=f"{10**(c_scale.get()/10):.12f}"))
c_scale.set(-120)
c_scale.pack()


## run button-------------------------------------------------
def run_program(adj, L, W, c, remaining_team, to_replace):
	current_team = remaining_team + to_replace
	new_members = replace_subteam_greedy(adj, L, W, c, current_team, to_replace)
	for name_id in new_members:
		add_to_list(name_id, replacements_found, replacements_found, results_random())

run_func = lambda: run_program(adj, L, W, float(c_value['text']), list(remaining_team.keys()), list(to_replace.keys()))
run_button = Button(master, text = "Run program", command=run_func, anchor='e')
run_button.grid(row=1, column = 3)
##---------------------------------------

master.mainloop()
