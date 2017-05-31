import sqlite3, sys
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from IPython import embed as IP
import numpy as np
import random
import time

class Result:

	def __init__(self, path_to_db, super_categories=False):
		self.db_path = path_to_db
		self.extractFromDatabase()
		self.directory = '/srv/result/matplot/'
		#self.userPrompt(super_categories)

	# Only for command line Testing.
	# def userPrompt(self, super_categories):
	# 	input=raw_input("Please select the plot type:\n1. Capacity\n2. Output Flow\n3. Emissions\n4. Exit\n")
	# 	while (input != '4'):
	# 		print "Please enter the sector name:"
			
	# 		sector_names = self.getSectors(int(input))
			
	# 		for i, s in enumerate(sector_names):
	# 			print str(i+1)+"."+s
			
	# 		sector_i = int(raw_input())-1
	# 		if (sector_i < 0 or sector_i >= len(sector_names)):
	# 			print "Invalid Input"
	# 			continue

	# 		sector = sector_names[sector_i]

	# 		if (input == '1'):
	# 			self.generatePlotForCapacity(sector, super_categories)
	# 		elif (input == '2'):
	# 			self.generatePlotForOutputFlow(sector, super_categories)
	# 		elif (input == '3'):
	# 			self.generatePlotForEmissions(sector, super_categories)
	# 		else:
	# 			print "Invalid Selection"
	# 		input=raw_input("Please select the plot type:\n1. Capacity\n2. Output Flow\n3. Emissions\n4. Exit\n")


	def extractFromDatabase(self):
		con = sqlite3.connect(self.db_path)
		cur = con.cursor()
		cur.execute("SELECT sector, t_periods, tech, capacity FROM Output_CapacityByPeriodAndTech")
		self.capacity_output = cur.fetchall()
		self.capacity_output = [list(elem) for elem in self.capacity_output]

		cur.execute("SELECT sector, t_periods, tech, SUM(vflow_out) FROM Output_VFlow_Out GROUP BY sector, t_periods, tech")	
		self.output_vflow = cur.fetchall()
		self.output_vflow = [list(elem) for elem in self.output_vflow]

		cur.execute("SELECT sector, t_periods, emissions_comm, SUM(emissions) FROM Output_Emissions GROUP BY sector, t_periods, emissions_comm")
		self.output_emissions = cur.fetchall()
		self.output_emissions = [list(elem) for elem in self.output_emissions]

		cur.execute("SELECT tech, tech_category FROM technologies")
		self.tech_categories = cur.fetchall()
		self.tech_categories = [[str(word) for word in tuple] for tuple in self.tech_categories]
		#self.tech_categories = []
		con.close()


	def getSectors(self, type):
		sectors = set()

		data = self.capacity_output

		if (type == 1):
			data = self.capacity_output
		elif (type == 2):
			data = self.output_vflow
		elif (type == 3):
			data = self.output_emissions

		for row in data:
			sectors.add(row[0])

		return list(sectors)

	def processData(self,inputData, sector, super_categories=False):
		periods = set()
		techs = set()

		for row in inputData:
			row[0] = str(row[0])
			row[1] = int(row[1])
			row[2] = str(row[2])
			row[3] = float(row[3])

		tech_dict = dict(self.tech_categories)
		if (super_categories):
			for row in inputData:
				row[2] = tech_dict.get(row[2],row[2])

		for row in inputData:
			if (row[0] == sector or sector=='all'):
				periods.add(row[1])  # Reminder: indexing starts at 0
				techs.add(row[2])

		periods = list(periods)
		techs = list(techs)
 		periods.sort()

		output_values = dict()   # Each row in a dictionary is a list
		for tech in techs:
			output_values[tech] = [0]*len(periods)    #this just creates a blank table
		for row in inputData:
			if (row[0] == sector or sector=='all'):
				output_values[row[2]][periods.index(row[1])] += row[-1]
		
		output_values['periods']=periods
		return output_values

	def generatePlotForCapacity(self,sector, super_categories=False):
		output_values = self.processData(self.capacity_output, sector, super_categories)
		outfile = 'capacity_'+sector+'_'+str(int(time.time()*1000))+'.png'
		self.output_file_name = self.directory + outfile
		self.output_file_name = self.output_file_name.replace(" ", "")
		title = 'Capacity Plot for ' + sector + ' sector'
		self.makeStackedBarPlot(output_values, "Years", "Capacity (GW)", 'periods', title)
		return outfile

	def generatePlotForOutputFlow(self, sector, super_categories=False):
		output_values = self.processData(self.output_vflow, sector, super_categories)
		outfile = 'output_flow_'+sector+'_'+str(int(time.time()*1000))+'.png'
		self.output_file_name = self.directory + outfile
		self.output_file_name = self.output_file_name.replace(" ", "")
		title = 'Output Flow Plot for ' + sector + ' sector'
		self.makeStackedBarPlot(output_values, "Years", "Activity (PJ)", 'periods', title)
		return outfile;

	def generatePlotForEmissions(self, sector, super_categories=False):
		output_values = self.processData(self.output_emissions, sector, super_categories)
		outfile ='emissions_'+sector+'_'+str(int(time.time()*1000))+'.png'
		self.output_file_name = self.directory + outfile
		self.output_file_name = self.output_file_name.replace(" ", "")
		title = 'Emissions Plot for ' + sector + ' sector'
		self.make_line_plot(output_values.copy(), 'Emissions', title)
		return outfile;
	

	def get_random_color(self, pastel_factor = 0.5):
	    return [(x+pastel_factor)/(1.0+pastel_factor) for x in [random.uniform(0,1.0) for i in [1,2,3]]]

	def color_distance(self, c1,c2):
	    return sum([abs(x[0]-x[1]) for x in zip(c1,c2)])

	def generate_new_color(self, existing_colors,pastel_factor = 0.5):
	    max_distance = None
	    best_color = None
	    for i in range(0,100):
	        color = self.get_random_color(pastel_factor = pastel_factor)
	        if not existing_colors:
	            return color
	        best_distance = min([self.color_distance(color,c) for c in existing_colors])
	        if not max_distance or best_distance > max_distance:
	            max_distance = best_distance
	            best_color = color
	    return best_color

	def makeStackedBarPlot(self, data, xlabel, ylabel, xvar, title):
		random.seed(10)

		handles = list()
		xaxis=data[xvar]
		data.pop('c',0)
		data.pop(xvar,0)
		stackedBars = data.keys()
		
		colorMapForBars=dict()
	  	colors = []
	  	plt.figure()
	  	for i in range(0,len(stackedBars)):
	  		colors.append(self.generate_new_color(colors,pastel_factor = 0.9))
			colorMapForBars[data.keys()[i]]=colors[i]
		
		width = 1.5
		b = [0]*len(xaxis)

		#plt.figure()

		for bar in stackedBars:
			h = plt.bar(xaxis, data[bar], width, bottom = b, color = colorMapForBars[bar])
			handles.append(h)
			b = [b[j] + data[bar][j] for j in range(0, len(b))]

		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		plt.xticks(xaxis)
		plt.title(title)
		lgd = plt.legend([h[0] for h in handles], stackedBars, bbox_to_anchor = (1.2, 1),fontsize=7.5)
		#plt.show()
		plt.savefig(self.output_file_name, bbox_extra_artists=(lgd,), bbox_inches='tight')

	def make_stacked_bar_plot(self, plot_var, label):
		handles = list()
		periods=plot_var['periods']
		plot_var.pop('c',0)
		plot_var.pop('periods',0)
		techs = plot_var.keys()
		random.seed(10)
		color_map=dict()
	  	colors = []
	  	plt.figure()
	  	for i in range(0,len(techs)):
	  		colors.append(self.generate_new_color(colors,pastel_factor = 0.9))
			color_map[plot_var.keys()[i]]=colors[i]
		width = 1.5

		b = [0]*len(periods)
		for tech in techs:
			h = plt.bar(periods, plot_var[tech], width, bottom = b, color = color_map[tech])
			handles.append(h)
			b = [b[j] + plot_var[tech][j] for j in range(0, len(b))]   #this stacks the bars

		plt.xlabel("Years")
		plt.ylabel(label)
		#plt.xticks([i + width*0.5 for i in periods], [str(i) for i in periods])
		plt.xticks(periods)
		lgd = plt.legend([h[0] for h in handles], techs, bbox_to_anchor = (1.2, 1),fontsize=7.5)
		#plt.show()
		plt.savefig(self.output_file_name, bbox_extra_artists=(lgd,), bbox_inches='tight')

	def make_line_plot(self, plot_var, label, title):
		handles = list()
		periods=plot_var['periods']
		plot_var.pop('periods',0)
		techs = plot_var.keys()
		random.seed(10)
		color_map=dict()
	  	colors = []
	  	width = 1.5
	  	plt.figure()
	  	for i in range(0,len(techs)):
	    		colors.append(self.generate_new_color(colors,pastel_factor = 0.9))
			color_map[plot_var.keys()[i]]=colors[i]

		b = [0]*len(periods)
		for tech in techs:
			h = plt.plot(periods, plot_var[tech],color = color_map[tech], linestyle='--', marker='o')
			handles.append(h)

		plt.xlabel("Years")
		plt.ylabel(label)
		#plt.xticks([i + width*0.5 for i in periods], [str(i) for i in periods])
		plt.xticks(periods)
		plt.title(title)
		lgd = plt.legend([h[0] for h in handles], techs, bbox_to_anchor = (1.2, 1),fontsize=7.5)
		#plt.show()
		plt.savefig(self.output_file_name, bbox_extra_artists=(lgd,), bbox_inches='tight')

