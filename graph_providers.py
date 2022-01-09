import csv
import xlrd
import openpyxl
import datetime
from time import gmtime, strftime
import urllib2
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import warnings
import ast
from prettytable import PrettyTable
import MySQLdb


my_bet = 5
base = 380
returns = {1:1.73,5:8.7,7:12,10:17.3,20:34.6,25:44.6,35:62.7,40:71.6,50:90.6,75:134.6,100:181.6,150:272.6,175:318.6,200:369.6,250:454.6,275:499.6,300:544.6,500:916.6}
#SQL_db = MySQLdb.connect(host="rommbot.ddns.net", user="#####",passwd="#####", db="binary_data") # name of the data base
SQL_db = MySQLdb.connect(host="localhost", user="#####",passwd="#####", db="binary_data") # name of the data base
cur = SQL_db.cursor()
start_date_string = "2018-08-01"
end_date_string = "2019-12-01"
date_time_string="%s %s" % (start_date_string,"00:00:00")
new_robot_name='Target_A'
my_robot_name='rommbot'
enableEventTriggers=False
bestProviders=[]
robotTraces ={}
robotResults ={}
results2 ={}
rank ={}
slope={}
ratio={}
num_trades={}
num_wins={}

colors=['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
		'#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
        '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
        '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5',	
		'#00ffbf', '#00ffff', '#00bfff', '#0080ff',	'#0040ff',
		'#80ff00', '#40ff00', '#00ff00', '#00ff40',	'#00ff80',		
		'#0000ff', '#4000ff', '#8000ff', '#bf00ff', '#ff00ff',
		'#ff4000', '#ff8000', '#ffbf00', '#ffff00', '#bfff00',
		'#80ff00', '#40ff00', '#00ff00', '#00ff40', '#00ff80',
		'#00ffbf', '#00ffff', '#00bfff', '#0080ff', '#0040ff',
		'#0000ff', '#4000ff', '#8000ff', '#bf00ff', '#ff00ff',
		'#ff00bf', '#ff0080', '#ff0040']

def getRobotResults():	
	s_previous_provider=""
	s_previous_date_time=datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")	
	sql = "select t.provider, t.close_date, t.win_loss from trade_history_new t where (t.close_date >= '%s' and t.close_date <= '%s') and t.provider != 'OMIA68' order by t.provider, t.close_date asc" % (start_date_string, end_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		#print row
		provider=row[0]
		if provider != s_previous_provider:
			s_previous_date_time=datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")	
		
		if (row[1] - s_previous_date_time).total_seconds() == 0:
			current_date_time = row[1] + datetime.timedelta(seconds=60)
		elif (row[1] - s_previous_date_time).total_seconds() < 0:	
			current_date_time = s_previous_date_time + datetime.timedelta(seconds=60)
		else:
			current_date_time = row[1]
		s_date=current_date_time.strftime("%Y-%m-%d %H:%M:%S").split(" ")[0]
		s_time=current_date_time.strftime("%Y-%m-%d %H:%M:%S").split(" ")[1]
		win_loss=int(row[2])
		if provider in robotResults.keys():
			if s_date in robotResults[provider].keys():
				previous_time=sorted(robotResults[provider][s_date])[len(robotResults[provider][s_date])-1]
				robotResults[provider][s_date][s_time]=win_loss
			else:			
				#Get previous result
				previous_date=sorted(robotResults[provider])[len(robotResults[provider])-1]
				previous_time=sorted(robotResults[provider][previous_date])[len(robotResults[provider][previous_date])-1]
				
				#Sum current win_loss value to previous result
				robotResults[provider][s_date]={}
				robotResults[provider][s_date][s_time]=win_loss
		else:
			robotResults[provider]={}
			robotResults[provider][s_date]={}
			robotResults[provider][s_date][s_time]=win_loss
			
		s_previous_date_time=current_date_time
		s_previous_provider=provider		

def getRobotTraces():	
	for provider in sorted(robotResults.keys()):
		for s_date in sorted(robotResults[provider].keys()):
			for s_time in sorted(robotResults[provider][s_date].keys()):
				win_loss=robotResults[provider][s_date][s_time]
				if provider in robotTraces.keys():
					if s_date in robotTraces[provider].keys():
						previous_time=sorted(robotTraces[provider][s_date])[len(robotTraces[provider][s_date])-1]
						robotTraces[provider][s_date][s_time]=round(robotTraces[provider][s_date][previous_time]+((win_loss*returns[my_bet])-my_bet),1)					
					else:			
						#Get previous result
						previous_date=sorted(robotTraces[provider])[len(robotTraces[provider])-1]
						previous_time=sorted(robotTraces[provider][previous_date])[len(robotTraces[provider][previous_date])-1]
						
						#Sum current win_loss value to previous result
						robotTraces[provider][s_date]={}
						robotTraces[provider][s_date][s_time]=round(robotTraces[provider][previous_date][previous_time]+((win_loss*returns[my_bet])-my_bet),1)
				else:
					robotTraces[provider]={}
					robotTraces[provider][s_date]={}
					robotTraces[provider][s_date][s_time]=round(base+((win_loss*returns[my_bet])-my_bet),1)
									
def getBestProviders():	
	for robot in sorted(rank, key=rank.get, reverse=True):
		if (rank[robot] != 0) and (ratio[robot] > 56) and num_trades[robot] >= 3 and robot not in ['rommbot','rommjp']:
			bestProviders.append(robot)
												
	#Build Target_1 Robot on best providers
	robotResults[new_robot_name]={}
	for s_robot in bestProviders:
		for s_date in sorted(robotResults[s_robot].keys()):
			for s_time in sorted(robotResults[s_robot][s_date].keys()):
				winloss=robotResults[s_robot][s_date][s_time]
				if s_date in robotResults[new_robot_name].keys():
					if s_time in robotResults[new_robot_name][s_date].keys():
						current_winloss=robotResults[new_robot_name][s_date][s_time]
						if winloss > current_winloss:
							robotResults[new_robot_name][s_date][s_time]=winloss
					else:
						robotResults[new_robot_name][s_date][s_time]=winloss
				else:
					robotResults[new_robot_name][s_date]={}	
					robotResults[new_robot_name][s_date][s_time]=winloss

	robotTraces[new_robot_name]={}				
	for robot_s in [new_robot_name]:
		for date in sorted(robotResults[robot_s].keys()):		
			for s_time in sorted(robotResults[robot_s][date].keys()):
				win_loss=robotResults[robot_s][date][s_time]
				if date in robotTraces[robot_s].keys():
					if len(robotTraces[robot_s][date].keys()) > 0:
						previous_time = sorted(robotTraces[robot_s][date].keys())[len(robotTraces[robot_s][date].keys())-1]
						previous_result = robotTraces[robot_s][date][previous_time]
						robotTraces[robot_s][date][s_time]=previous_result+((win_loss*returns[my_bet])-my_bet)
				else:
					robotTraces[robot_s][date]={}
					try:
						previous_date = sorted(robotTraces[robot_s].keys())[len(sorted(robotTraces[robot_s].keys()))-2]
						previous_time = sorted(robotTraces[robot_s][previous_date].keys())[len(sorted(robotTraces[robot_s][previous_date].keys()))-1]
						previous_result = robotTraces[robot_s][previous_date][previous_time]
						robotTraces[robot_s][date][s_time]=previous_result+((win_loss*returns[my_bet])-my_bet)
					except IndexError:
						robotTraces[robot_s][date][s_time]=base+((win_loss*returns[my_bet])-my_bet)

	for robot_s in [new_robot_name]:
		datetime_array=[]
		values_array=[]
		for s_date in sorted(robotTraces[robot_s].keys()):	
			for s_time in sorted(robotTraces[robot_s][s_date].keys()):
				date_time_string = s_date+" "+s_time
				values_array.append(robotTraces[robot_s][s_date][s_time])
				datetime_array.append(datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S"))
		converted_dates_array = mdates.date2num(datetime_array)
		try:
			coefficients = np.polyfit(converted_dates_array, values_array, 1)
			polynomial = np.poly1d(coefficients)
			slope[robot_s]=round(coefficients[0],1)
		except TypeError:
			slope[robot_s]=0
	
	for robot_s in [new_robot_name]:
		total_wins=0
		total_trades=0
		profit=0
		wins=0	
		bets=0
		for date in robotResults[robot_s].keys():
			values = robotResults[robot_s][date].values()
			wins+=sum(values)
			bets+=len(values)
			total_trades=total_trades+len(values)
			total_wins=wins
		try:
			ratio[robot_s]=	round((float(wins)/float(total_trades))*100,1)
		except ZeroDivisionError:
			ratio[robot_s]=0	
		num_wins[robot_s]=wins
		num_trades[robot_s]=total_trades
		profit = wins*returns[my_bet] - my_bet*total_trades
		rank[robot_s]=profit

def getStats():	
	for bot in robotResults.keys():
		datetime_array=[]
		values_array=[]		
		total_wins=0
		total_trades=0
		profit=0
		wins=0	
		bets=0
		for date in sorted(robotResults[bot].keys()):
			values = robotResults[bot][date].values()	
			wins+=sum(values)
			bets+=len(values)
			total_trades=total_trades+len(values)
			total_wins=total_wins+wins
		try:
			ratio[bot]=round((float(wins)/float(total_trades))*100,1)
		except ZeroDivisionError:
			ratio[bot]=0
		num_wins[bot]=wins
		num_trades[bot]=total_trades
		profit = wins*returns[my_bet] - my_bet*total_trades
		rank[bot]=profit		
		#Get slope for robotrace
		try:
			for s_date in sorted(robotTraces[bot].keys()):
				current_date = s_date.split("-") 	
				for s_time in sorted(robotTraces[bot][s_date].keys()):
					date_time_string = s_date+" "+s_time
					values_array.append(robotTraces[bot][s_date][s_time])
					datetime_array.append(datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S"))
			if len(datetime_array) > 0 and len(values_array) > 0:
				converted_dates_array = mdates.date2num(datetime_array)
				try:
					coefficients = np.polyfit(converted_dates_array, values_array, 1)
					polynomial = np.poly1d(coefficients)
					slope[bot]=round(coefficients[0],1)
				except TypeError:
					slope[bot]=0	
			else:
				slope[bot]=0
		except KeyError:
			slope[bot]=0	

def getEventMarkers():
	markers=[]
	sql="select e.providers, e.`action`, e.datetime_stamp, e.comments from event_tracker e where e.datetime_stamp >= '%s' and  e.datetime_stamp <= '%s' order by e.datetime_stamp asc"%(start_date_string, end_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		markers.append([row[0], row[1], row[2], row[3]])
	return markers
			
def plotRobots():
	index=0		
	for robot in sorted(rank, key=rank.get, reverse=True):
		datetime_array=[]
		values_array=[]
		if robot==my_robot_name:
			g_color='#000000'
		elif robot=='rommjp':	
			g_color='#800080'				
		else:
			if robot==new_robot_name:
				g_color='#ff0000'
			else:
				if colors[index] in ['#800080','#ff0000','#000000']:
					index=index+1 
				g_color = colors[index]
		
		if robot in bestProviders:
			robot_name='+'+robot
			marker_type='+'
		else:
			robot_name=robot
			marker_type='o'
		for s_date in sorted(robotTraces[robot].keys()):
			current_date = s_date.split("-")
			for s_time in sorted(robotTraces[robot][s_date].keys()):
				date_time_string = s_date+" "+s_time
				#print date_time_string, robotTraces[robot][s_date][s_time]
				values_array.append(robotTraces[robot][s_date][s_time])
				datetime_array.append(datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S"))
		legend_string = "%s [%s,%s%%] (%s, %s)" %(robot_name, str(num_trades[robot]),str(ratio[robot]), str(rank[robot]), str(slope[robot]	))
		plt.plot(datetime_array, values_array, g_color, label=legend_string, marker=marker_type)
		index=index+1
	#plt.legend(bbox_to_anchor=(0.90, 1), loc=2, borderaxespad=0.)
	plt.suptitle('GMT: '+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+'\n Start date: '+ start_date_string+', End date: '+ end_date_string, fontsize=14, fontweight='bold')
	markers = getEventMarkers()
	if (len(markers) > 0) and enableEventTriggers:
		for marker in markers:
			provider=marker[0]
			action=marker[1]
			datetime_stamp=marker[2]
			comments=marker[3]
			if action=='ADD':
				plt.axvline(x=datetime_stamp, color='green', label="%s @ %s (%s)"%(provider,datetime_stamp.strftime("%Y-%m-%d %H:%M:%S"),comments))
			elif action=='REMOVE':
				plt.axvline(x=datetime_stamp, color='red', label="%s @ %s (%s)"%(provider,datetime_stamp.strftime("%Y-%m-%d %H:%M:%S"),comments))
	plt.legend(loc='best')
	plt.show()

getRobotResults()
getRobotTraces()
getStats()
getBestProviders()
plotRobots()
#runSimulation()


