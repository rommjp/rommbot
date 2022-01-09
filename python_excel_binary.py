'''
Created 4/06/2016 -- R.Poggenberg
'''

import os 
import csv
import xlrd
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
#from sklearn.svn import SVR

warnings.simplefilter('ignore', np.RankWarning)

rank ={}
slope={}
ratio={}
num_trades={}
num_wins={}
bestProviders=[]
h_rank={}
h_ratio={}
h_num_trades={}
h_num_wins={}
results ={}
results2 ={}
history_data={}
rommjp_data={}
robotTraces ={}
profit_delta={}
my_bet = 5
base = 250
trade_window=40
returns = {1:1.8,5:8.6,7:12,10:18,20:36,25:45,35:63,40:72,50:91,75:135,100:182,150:273,175:319,200:370,250:455,275:500,300:545,500:917}
start_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday()) #Use Current Monday of the week as startime
#start_date = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
#start_date = datetime.datetime.utcnow().date()
gmt_date = datetime.datetime.utcnow().date()
new_robot_name='Target_A'
my_robot_name='rommbot'
path= 'C:\\Users\\rommj\\Downloads'
SQL_db = MySQLdb.connect(host="localhost", user="#####",passwd="#####", db="binary_data") # name of the data base
cur = SQL_db.cursor()

#Data members for trade4meAPI
selectROBOTS=[]
activeRobots={}
r_activeRobots={}
r_subscribedRobots={}
r_subscribedRobots_username={}
subscribedRobots={}
getSubscriptions="https://trade4.me/getSubscriptions.php?username=%s&password=gamboa85"%(my_robot_name)	
getActiveCopy="https://trade4.me/getActiveCopy.php?username=%s&password=gamboa85"%(my_robot_name)	
startCopy="https://trade4.me/startCopy.php?username=%s&password=gamboa85"%(my_robot_name)	
stopCopy="https://trade4.me/stopCopy.php?username=%s&password=gamboa85"%(my_robot_name)	
removeList={}
addList={}

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
		
		
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	   'Accept-Encoding': 'none',
	   'Accept-Language': 'en-US,en;q=0.8',
	   'Connection': 'keep-alive'}

event_data = {'Daily': {'ADD':{}, 'REMOVE':{}},
			  'Weekly':{'ADD':{}, 'REMOVE':{}}}	   
	   
def getLastTrades(trade_window):
	url = "https://trade4.me/history.php?username=%s&password=gamboa85&fetch=%s"%(my_robot_name, str(trade_window))
	
	req = urllib2.Request(url, headers=hdr)

	rank={}
	all_data=[]
	total_wins=0
	total_trades=0

	try:
		page = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		response= e.fp.read()
		for i, row in enumerate(response.split("<tr>")):
			data=[]
			if i > 1:
				for idx, column in enumerate(row.split("</td>")):
					if (idx==5 or idx==7 or idx==10):
						if idx==5:
							extract = column.split(">")
							data.append(extract[len(extract)-1])
						if idx==7:	
							extract = column.split("/")
							data.append(extract[len(extract)-2][:-6])
						if idx==10:	
							extract = column.split(">")
							data.append(extract[len(extract)-2][:-3])
				all_data.append(data)
	
	all_data = sorted(all_data, key=lambda x: x[0], reverse=True)
	#pprint(all_data)
	for row in all_data:
		current_date = row[0].split(' ')[0].split("-")
		if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 	
			if row[1] != 'pending':
				robot_s = row[2]
				if robot_s not in results.keys():
					results[robot_s]=[]
				win_loss = 1 if row[1] == 'won' else 0 if row[1] =='loss' else 0 #determine win loss value
				win_loss_array = results[robot_s]
				win_loss_array.append(win_loss)
				results[robot_s]=win_loss_array	
			
	for key in results:
		rank[key]=[sum(results[key])*(returns[my_bet]-my_bet) - (len(results[key])-sum(results[key]))*my_bet,len(results[key])]

	print "-----------------"		
	print "Last %s Trades on %s between %s - %s" % (str(trade_window), all_data[0][0].split(' ')[0], all_data[0][0].split(' ')[1],all_data[len(all_data)-1][0].split(' ')[1])
	print "-----------------"	
	for key in sorted(rank, key=rank.get, reverse=True):
		trades="("+str(rank[key][1])+")"
		print key, rank[key][0],trades
		total_wins+=rank[key][0]
		total_trades+=rank[key][1]
	print "-----------------"
	print "Net: "+str(total_wins)+" ("+str(total_trades)+")"

def getRobotData():
	spreadsheets=['Trading_history_with_tabs', 'Trading_history_with_tabs (1)', 'Trading_history_with_tabs (2)', 'Trading_history_with_tabs (3)', 'Trading_history', 'Trading_history (1)']
	for sheet in spreadsheets:
		#Open the workbook
		#wb = xlrd.open_workbook(sheet+'.xls')
		wb = xlrd.open_workbook(path+'\\'+sheet+'.xls')
		#get robot names
		if sheet in ['Trading_history']:
			robots=[my_robot_name]
		elif sheet in ['Trading_history (1)']:
			robots=['rommjp']	
		else:
			robots=wb.sheet_names()
		for idx, robot in enumerate(robots):
			robot_s = robot.encode('ascii','ignore') 
			sh = wb.sheet_by_index(idx)
			results[robot_s]={}
			results2[robot_s]={}
			datetime_list={}
			for rownum in range(sh.nrows):			
				if rownum > 0:
					row = sh.row_values(rownum)
					if row[7] != 'pending':
						date_value=str(datetime.datetime(*xlrd.xldate_as_tuple(row[5], wb.datemode)))
						win_loss = 1 if row[7] == 'won' else 0 if row[7] =='loss' else 0 #determine win loss value
						s_source = row[10]
						date = date_value.split(' ')[0]
						s_time = date_value.split(' ')[1]
						if date in datetime_list.keys():
							if s_time == '00:00:00':
								if len(datetime_list[date].keys()) > 0:
									rownum_list = sorted(datetime_list[date].keys())
									last_s_time = datetime_list[date][rownum_list[len(rownum_list)-1]]
									date_time_string="%s %s" % (date,last_s_time)
									previous_datetime=datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
									current_date_time = previous_datetime - datetime.timedelta(seconds=3)
									s_time = current_date_time.strftime('%H:%M:%S')
									datetime_list[date][rownum]=s_time
								else:
									date_list = sorted(datetime_list.keys())
									last_date = date_list[len(date_list)-1]
									rownum_list = sorted(datetime_list[last_date].keys())
									last_s_time = datetime_list[date][rownum_list[len(rownum_list)-1]]
									date_time_string="%s %s" % (date,last_s_time)
									previous_datetime=datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
									current_date_time = previous_datetime - datetime.timedelta(seconds=3)
									s_time = current_date_time.strftime('%H:%M:%S')
									datetime_list[date][rownum]=s_time									
							else:
								datetime_list[date][rownum]=s_time
									
						else:
							datetime_list[date]={}
							datetime_list[date][rownum]=s_time
						
						#if robot_s ==my_robot_name:
						#	print robot_s, date_value, s_time
						if date in results[robot_s].keys():
							win_loss_array = results[robot_s][date]
							win_loss_array.append(win_loss)	
							results[robot_s][date]=win_loss_array
						else:
							results[robot_s][date]=[win_loss]
						
						#Fill out results against time
						if date in results2[robot_s].keys(): 
							results2[robot_s][date][s_time]=win_loss
						else:
							results2[robot_s][date]={}	
							results2[robot_s][date][s_time]=win_loss
							
							
						if robot_s in [my_robot_name]:
							#Fill out results against time
							if robot_s in history_data.keys():
								if date in history_data[robot_s].keys(): 
									history_data[robot_s][date][s_time]=win_loss
								else:
									history_data[robot_s][date]={}	
									history_data[robot_s][date][s_time]=win_loss	
							else:
								history_data[robot_s]={}
								history_data[robot_s][date]={}	
								history_data[robot_s][date][s_time]=win_loss								
						
							source_array = s_source.split('from')
							if len(source_array) > 1:
								s_provider = source_array[1].strip()
							else:
								source_array = s_source.split('/')
								s_user_name = source_array[len(source_array)-1].strip()
								try:
									s_provider = subscribedRobots[s_user_name]['display_name']
								except KeyError:
									s_provider = s_user_name
								
							if s_provider in history_data.keys():
								if date in history_data[s_provider].keys():
									if s_time in history_data[s_provider][date].keys():
										date_time_string="%s %s" % (date,s_time)
										previous_datetime=datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
										current_date_time = previous_datetime + datetime.timedelta(seconds=1)
										new_s_time = current_date_time.strftime('%H:%M:%S')										
										history_data[s_provider][date][new_s_time]=win_loss
									else:
										history_data[s_provider][date][s_time]=win_loss	
								else:
									history_data[s_provider][date]={}
									history_data[s_provider][date][s_time]=win_loss
							else:
								history_data[s_provider]={}
								history_data[s_provider][date]={}			
								history_data[s_provider][date][s_time]=win_loss

						if robot_s in ['rommjp']:
							#Fill out results against time
							if robot_s in rommjp_data.keys():
								if date in rommjp_data[robot_s].keys(): 
									rommjp_data[robot_s][date][s_time]=win_loss
								else:
									rommjp_data[robot_s][date]={}	
									rommjp_data[robot_s][date][s_time]=win_loss	
							else:
								rommjp_data[robot_s]={}
								rommjp_data[robot_s][date]={}	
								rommjp_data[robot_s][date][s_time]=win_loss								
						
							source_array = s_source.split('from')
							if len(source_array) > 1:
								s_provider = source_array[1].strip()
							else:
								source_array = s_source.split('/')
								s_user_name = source_array[len(source_array)-1].strip()
								try:
									s_provider = subscribedRobots[s_user_name]['display_name']
								except KeyError:
									s_provider = s_user_name
								
							if s_provider in rommjp_data.keys():
								if date in rommjp_data[s_provider].keys():
									if s_time in rommjp_data[s_provider][date].keys():
										date_time_string="%s %s" % (date,s_time)
										previous_datetime=datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
										current_date_time = previous_datetime + datetime.timedelta(seconds=1)
										new_s_time = current_date_time.strftime('%H:%M:%S')										
										rommjp_data[s_provider][date][new_s_time]=win_loss
									else:
										rommjp_data[s_provider][date][s_time]=win_loss	
								else:
									rommjp_data[s_provider][date]={}
									rommjp_data[s_provider][date][s_time]=win_loss
							else:
								rommjp_data[s_provider]={}
								rommjp_data[s_provider][date]={}			
								rommjp_data[s_provider][date][s_time]=win_loss								
	for robot_s in rommjp_data:
		if robot_s in results.keys():
			results[robot_s]={}
			results2[robot_s]={}
			for s_date in rommjp_data[robot_s].keys():
				results[robot_s][s_date]={}
				results2[robot_s][s_date]={}			
				results[robot_s][s_date]=rommjp_data[robot_s][s_date].values()
				for s_time in rommjp_data[robot_s][s_date].keys(): 
					results2[robot_s][s_date][s_time]=rommjp_data[robot_s][s_date][s_time]
		else:
			results[robot_s]={}
			results2[robot_s]={}
			for s_date in rommjp_data[robot_s].keys():
				results[robot_s][s_date]={}
				results2[robot_s][s_date]={}				
				results[robot_s][s_date]=rommjp_data[robot_s][s_date].values()
				for s_time in rommjp_data[robot_s][s_date].keys():
					results2[robot_s][s_date][s_time]=rommjp_data[robot_s][s_date][s_time]
								
								
def getRank():
	for bot in results:	
		total_wins=0
		total_trades=0
		profit=0
		wins=0	
		bets=0
		for date, values in results[bot].iteritems():
			current_date = date.split("-")
			if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 
				wins+=sum(values)
				bets+=len(values)
				total_trades=total_trades+len(values)
			total_wins=total_wins+wins
		try:
			ratio[bot]=	round((float(wins)/float(total_trades))*100,1)
		except ZeroDivisionError:
			ratio[bot]=0
		num_wins[bot]=wins	
		num_trades[bot]=total_trades
		profit = wins*(returns[my_bet]-my_bet) - (bets-wins)*my_bet
		rank[bot]=profit
		
def getHistory():
	for bot in history_data.keys():
		total_wins=0
		total_trades=0
		profit=0
		wins=0	
		bets=0
		for date in sorted(history_data[bot].keys()):
			values = history_data[bot][date].values()
			current_date = date.split("-")
			if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 
				wins+=sum(values)
				bets+=len(values)
				total_trades=total_trades+len(values)
			total_wins=total_wins+wins
		try:
			h_ratio[bot]=round((float(wins)/float(total_trades))*100,1)
		except ZeroDivisionError:
			h_ratio[bot]=0
		h_num_wins[bot]=wins
		h_num_trades[bot]=total_trades
		profit = wins*(returns[my_bet]-my_bet) - (bets-wins)*my_bet
		h_rank[bot]=profit		

def printMonthlyReport(bots):

	if (new_robot_name in bots) and len(bots) > 1:
		bots.remove(new_robot_name)

	if (my_robot_name in bots) and len(bots) > 1:
		bots.remove(my_robot_name)

	for bot in results.keys():
		if bot in bots[0]:
			net_trades=0
			grand_total=0
			grand_profit_A=0
			grand_profit_B=0
			grand_profit_C=0
			grand_profit_D=0
			grand_profit_E=0
			grand_profit_F=0
			grand_profit_G=0
			grand_profit_H=0
			grand_profit_I=0
			grand_profit_J=0
			grand_profit_K=0
			grand_profit_L=0
			net_base=base
			if len(bots) == 12:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' '+bots[5]+' '+bots[6]+' '+bots[7]+' '+bots[8]+' '+bots[9]+' '+bots[10]+' '+bots[11]+' Total'									
			elif len(bots) == 11:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' '+bots[5]+' '+bots[6]+' '+bots[7]+' '+bots[8]+' '+bots[9]+' '+bots[10]+' Total'						
			elif len(bots) == 10:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' '+bots[5]+' '+bots[6]+' '+bots[7]+' '+bots[8]+' '+bots[9]+' Total'			
			elif len(bots) == 9:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' '+bots[5]+' '+bots[6]+' '+bots[7]+' '+bots[8]+' Total'									
			elif len(bots) == 8:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' '+bots[5]+' '+bots[6]+' '+bots[7]+' Total'						
			elif len(bots) == 7:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' '+bots[5]+' '+bots[6]+' Total'			
			elif len(bots) == 6:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' '+bots[5]+' Total'				
			elif len(bots) == 5:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' '+bots[4]+' Total'			
			elif len(bots) == 4:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' '+bots[3]+' Total'
			elif len(bots) == 3:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' '+bots[2]+' Total'
			elif len(bots) == 2:
				print 'Date'+'\t\t'+bots[0]+' '+bots[1]+' Total'				
			else:
				print 'Date'+'\t\t'+bots[0]+'\t'+'Trades'+'\t'+'Total'
			for date, values in sorted(results[bot].iteritems()):
				current_date = date.split("-")
				if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date:
					total=0
					profit_A=0
					profit_B=0
					profit_C=0
					profit_D=0
					profit_E=0
					profit_F=0
					profit_G=0
					profit_H=0
					profit_I=0
					profit_J=0
					profit_K=0
					profit_L=0
					num_trades = len(values)
					profit_A = sum(values)*(returns[my_bet]-my_bet) - (len(values)-sum(values))*my_bet
					if len(bots) > 1:
						try:
							profit_B = sum(results[bots[1]][date])*(returns[my_bet]-my_bet) - (len(results[bots[1]][date])-sum(results[bots[1]][date]))*my_bet
						except KeyError:
							profit_B=0
								
						try:
							if len(bots) > 2:
								profit_C = sum(results[bots[2]][date])*(returns[my_bet]-my_bet) - (len(results[bots[2]][date])-sum(results[bots[2]][date]))*my_bet
							else:
								profit_C=0
						except KeyError:
							profit_C=0
								
						try:
							if len(bots) > 3:
								profit_D = sum(results[bots[3]][date])*(returns[my_bet]-my_bet) - (len(results[bots[3]][date])-sum(results[bots[3]][date]))*my_bet
							else:
								profit_D=0
						except KeyError:
							profit_D=0	
							
						try:
							if len(bots) > 4:
								profit_E = sum(results[bots[4]][date])*(returns[my_bet]-my_bet) - (len(results[bots[4]][date])-sum(results[bots[4]][date]))*my_bet
							else:
								profit_E=0
						except KeyError:
							profit_E=0	

						try:
							if len(bots) > 5:
								profit_F = sum(results[bots[5]][date])*(returns[my_bet]-my_bet) - (len(results[bots[5]][date])-sum(results[bots[5]][date]))*my_bet
							else:
								profit_F=0
						except KeyError:
							profit_F=0	
							
						try:
							if len(bots) > 6:
								profit_G = sum(results[bots[6]][date])*(returns[my_bet]-my_bet) - (len(results[bots[6]][date])-sum(results[bots[6]][date]))*my_bet
							else:
								profit_G=0
						except KeyError:
							profit_G=0
							
						try:
							if len(bots) > 7:
								profit_H = sum(results[bots[7]][date])*(returns[my_bet]-my_bet) - (len(results[bots[7]][date])-sum(results[bots[7]][date]))*my_bet
							else:
								profit_H=0
						except KeyError:
							profit_H=0	

						try:
							if len(bots) > 8:
								profit_I = sum(results[bots[8]][date])*(returns[my_bet]-my_bet) - (len(results[bots[8]][date])-sum(results[bots[8]][date]))*my_bet
							else:
								profit_I=0
						except KeyError:
							profit_I=0	
							
						try:
							if len(bots) > 9:
								profit_J = sum(results[bots[9]][date])*(returns[my_bet]-my_bet) - (len(results[bots[9]][date])-sum(results[bots[9]][date]))*my_bet
							else:
								profit_J=0
						except KeyError:
							profit_J=0	
							
						try:
							if len(bots) > 10:
								profit_K = sum(results[bots[10]][date])*(returns[my_bet]-my_bet) - (len(results[bots[10]][date])-sum(results[bots[10]][date]))*my_bet
							else:
								profit_K=0
						except KeyError:
							profit_K=0

						try:
							if len(bots) > 11:
								profit_L = sum(results[bots[11]][date])*(returns[my_bet]-my_bet) - (len(results[bots[11]][date])-sum(results[bots[11]][date]))*my_bet
							else:
								profit_L=0
						except KeyError:
							profit_L=0								
							
									
					total=profit_A+profit_B+profit_C+profit_D+profit_E+profit_F+profit_G+profit_H+profit_I+profit_J+profit_K+profit_L
					net_base=net_base+total
					grand_profit_A+=profit_A
					grand_profit_B+=profit_B			
					grand_profit_C+=profit_C
					grand_profit_D+=profit_D
					grand_profit_E+=profit_E
					grand_profit_F+=profit_F
					grand_profit_G+=profit_G
					grand_profit_H+=profit_H
					grand_profit_I+=profit_I
					grand_profit_J+=profit_J
					grand_profit_K+=profit_K
					grand_profit_L+=profit_L
					grand_total+=total
					net_trades+=num_trades
					
					if len(bots) == 12:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(profit_F)+"\t"+str(profit_G)+"\t"+str(profit_H)+"\t"+str(profit_I)+'\t'+str(profit_J)+'\t'+str(profit_K)+'\t'+str(profit_L)+'\t'+str(total)+'\t'+str(net_base)																		
					elif len(bots) == 11:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(profit_F)+"\t"+str(profit_G)+"\t"+str(profit_H)+"\t"+str(profit_I)+'\t'+str(profit_J)+'\t'+str(profit_K)+'\t'+str(total)+'\t'+str(net_base)																		
					elif len(bots) == 10:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(profit_F)+"\t"+str(profit_G)+"\t"+str(profit_H)+"\t"+str(profit_I)+'\t'+str(profit_J)+'\t'+str(total)+'\t'+str(net_base)																		
					elif len(bots) == 9:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(profit_F)+"\t"+str(profit_G)+"\t"+str(profit_H)+"\t"+str(profit_I)+'\t'+str(total)+'\t'+str(net_base)													
					elif len(bots) == 8:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(profit_F)+"\t"+str(profit_G)+"\t"+str(profit_H)+'\t'+str(total)+'\t'+str(net_base)								
					elif len(bots) == 7:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(profit_F)+"\t"+str(profit_G)+'\t'+str(total)+'\t'+str(net_base)								
					elif len(bots) == 6:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(profit_F)+"\t"+str(total)+'\t'+str(net_base)				
					elif len(bots) == 5:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+'\t'+str(profit_E)+"\t"+str(total)+'\t'+str(net_base)				
					elif len(bots) == 4:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+'\t'+str(profit_D)+"\t"+str(total)+'\t'+str(net_base)
					elif len(bots) == 3:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+'\t'+str(profit_C)+"\t"+str(total)+'\t'+str(net_base)			
					elif len(bots) == 2:
						print date+'\t'+str(profit_A)+'\t'+str(profit_B)+"\t"+'\t'+str(total)+'\t'+str(net_base)
					else:
						print date+'\t'+str(profit_A)+"\t ("+str(num_trades)+")"+'\t'+str(net_base) 

			if len(bots) == 12:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_profit_F)+'\t'+str(grand_profit_G)+'\t'+str(grand_profit_H)+'\t'+str(grand_profit_I)+'\t'+str(grand_profit_J)+'\t'+str(grand_profit_K)+'\t'+str(grand_profit_L)+'\t'+str(grand_total)															
			elif len(bots) == 11:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_profit_F)+'\t'+str(grand_profit_G)+'\t'+str(grand_profit_H)+'\t'+str(grand_profit_I)+'\t'+str(grand_profit_J)+'\t'+str(grand_profit_K)+'\t'+str(grand_total)									
			elif len(bots) == 10:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_profit_F)+'\t'+str(grand_profit_G)+'\t'+str(grand_profit_H)+'\t'+str(grand_profit_I)+'\t'+str(grand_profit_J)+'\t'+str(grand_total)			
			elif len(bots) == 9:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_profit_F)+'\t'+str(grand_profit_G)+'\t'+str(grand_profit_H)+'\t'+str(grand_profit_I)+'\t'+str(grand_total)			
			elif len(bots) == 8:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_profit_F)+'\t'+str(grand_profit_G)+'\t'+str(grand_profit_H)+'\t'+str(grand_total)			
			elif len(bots) == 7:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_profit_F)+'\t'+str(grand_profit_G)+'\t'+str(grand_total)			
			elif len(bots) == 6:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_profit_F)+'\t'+str(grand_total)			
			elif len(bots) == 5:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_profit_E)+'\t'+str(grand_total)			
			elif len(bots) == 4:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_profit_D)+'\t'+str(grand_total)					
			elif len(bots) == 3:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_profit_C)+'\t'+str(grand_total)
			elif len(bots) == 2:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+str(grand_profit_B)+'\t'+str(grand_total)				
			else:
				print 'Total'+'\t\t'+str(grand_profit_A)+'\t'+"("+str(net_trades)+")"

						
def getRobotTrace():
	for robot_s in results2.keys():
		robotTraces[robot_s]={}
		for date in sorted(results2[robot_s].keys()):
			current_date = date.split("-")
			if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 		
				for s_time in sorted(results2[robot_s][date].keys()):
					win_loss=results2[robot_s][date][s_time]
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

def getSlope():	
	for robot in rank.keys():
		datetime_array=[]
		values_array=[]
		try:
			for s_date in sorted(robotTraces[robot].keys()):
				current_date = s_date.split("-")
				if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 	
					for s_time in sorted(robotTraces[robot][s_date].keys()):
						date_time_string = s_date+" "+s_time
						values_array.append(robotTraces[robot][s_date][s_time])
						datetime_array.append(datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S"))
			if len(datetime_array) > 0 and len(values_array) > 0:
				converted_dates_array = mdates.date2num(datetime_array)
				try:
					coefficients = np.polyfit(converted_dates_array, values_array, 1)
					polynomial = np.poly1d(coefficients)
					slope[robot]=round(coefficients[0],1)
				except TypeError:
					slope[robot]=0	
			else:
				slope[robot]=0
		except KeyError:
			slope[robot]=0
	
def getBestProviders():	
	for robot in sorted(rank, key=rank.get, reverse=True):
		if (rank[robot] != 0) and (ratio[robot] >= 58) and num_trades[robot] >= 4 and robot not in ['rommbot','rommjp']:
			bestProviders.append(robot)
												
	#Build Target_1 Robot on best providers
	results2[new_robot_name]={}
	for s_robot in bestProviders:
		for s_date in sorted(results2[s_robot].keys()):
			for s_time in sorted(results2[s_robot][s_date].keys()):
				winloss=results2[s_robot][s_date][s_time]
				if s_date in results2[new_robot_name].keys():
					if s_time in results2[new_robot_name][s_date].keys():
						current_winloss=results2[new_robot_name][s_date][s_time]
						if winloss > current_winloss:
							results2[new_robot_name][s_date][s_time]=winloss
					else:
						results2[new_robot_name][s_date][s_time]=winloss
				else:
					results2[new_robot_name][s_date]={}	
					results2[new_robot_name][s_date][s_time]=winloss
	
	results[new_robot_name]={}
	for robot_s in [new_robot_name]:
		for s_date in results2[new_robot_name]:
			for s_time in results2[new_robot_name][s_date]:
				win_loss=results2[new_robot_name][s_date][s_time]
				if s_date in results[robot_s].keys():
					win_loss_array = results[robot_s][s_date]
					win_loss_array.append(win_loss)	
					results[robot_s][s_date]=win_loss_array
				else:
					results[robot_s][s_date]=[win_loss]				

	for robot_s in [new_robot_name]:
		robotTraces[robot_s]={}
		for date in sorted(results2[robot_s].keys()):
			current_date = date.split("-")
			if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 		
				for s_time in sorted(results2[robot_s][date].keys()):
					win_loss=results2[robot_s][date][s_time]
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
			current_date = s_date.split("-")
			if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 	
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
		for date, values in results[robot_s].iteritems():
			current_date = date.split("-")
			if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 
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
		profit = wins*(returns[my_bet]-my_bet) - (bets-wins)*my_bet
		rank[robot_s]=profit
	
def plotRobots():
	index=0		
	for robot in sorted(rank, key=rank.get, reverse=True):		
		if (rank[robot] != 0) and (rank[robot] > -100):
			datetime_array=[]
			values_array=[]
			if robot==my_robot_name:
				g_color='#000000'
			else:
				if robot==new_robot_name:
					g_color='#ff0000'
				else:
					g_color = colors[index]
			
			if robot in bestProviders:
				robot_name='+'+robot
				marker_type='+'
			else:
				robot_name=robot
				marker_type='o'
			for s_date in sorted(robotTraces[robot].keys()):
				current_date = s_date.split("-")
				if datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2])) >= start_date: 	
					for s_time in sorted(robotTraces[robot][s_date].keys()):
						date_time_string = s_date+" "+s_time
						#print date_time_string, robotTraces[robot][s_date][s_time]
						values_array.append(robotTraces[robot][s_date][s_time])
						datetime_array.append(datetime.datetime.strptime(date_time_string, "%Y-%m-%d %H:%M:%S"))
			legend_string = "%s [%s,%s%%] (%s, %s)" %(robot_name, str(num_trades[robot]),str(ratio[robot]), str(rank[robot]), str(slope[robot]	))
			plt.plot(datetime_array, values_array, g_color, label=legend_string, marker=marker_type)
			index=index+1
	#plt.legend(bbox_to_anchor=(0.90, 1), loc=2, borderaxespad=0.)
	plt.suptitle('GMT: '+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+'\n Start date: '+ start_date.strftime("%a, %d %b %Y %H:%M:%S"), fontsize=14, fontweight='bold')
	plt.legend(loc='best')
	plt.show()	

def get_from_trade4me(api): 	
	data={}
	
	req = urllib2.Request(api, headers=hdr)
		
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		response= e.fp.read()
		if api==getActiveCopy:
			data = ast.literal_eval(response)
		elif api==getSubscriptions:
			returnedData = ast.literal_eval(response)
			for element in returnedData:
				for robot in element:
					#print robot, element[robot]	
					data[robot]=element[robot]	
		
	return data	
	
def post_to_trade4me(api, robot):
	data={}
	
	if api==stopCopy:
		send_api = api+"&provider=%s" %(robot)
	elif api==startCopy:
		send_api = api+"&provider=%s&amount=%s"%(robot, str(my_bet))	
	
	req = urllib2.Request(send_api, headers=hdr)
		
	try:
		page = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		response= e.fp.read()
		data['response'] = response
			
	return data

def saveEvents(robots, event):
	robot_string=""
	comment_string=''
	
	if len(robots) > 1:
		robot_string=";".join(str(x) for x in robots.keys())
		comment_string=";".join(str(x) for x in robots.values())
	else:
		robot_string=robots.keys()[0]
		comment_string=robots.values()[0]
		
	sql = "INSERT INTO event_tracker (providers, action, comments, datetime_stamp) \
				VALUES ('%s', '%s', '%s', '%s')" % (robot_string, event, comment_string, strftime('%Y-%m-%d %H:%M:%S', gmtime()))
				
	cur.execute(sql)
	SQL_db.commit()		
	
def stopProviders():
	print "\n ##########################################################################################"
	print " Remove Providers"
	print " ##########################################################################################"
	#Stop providers
	for provider in removeList.keys():
		try:
			response = post_to_trade4me(stopCopy,r_subscribedRobots_username[provider])
		except KeyError:
			response = post_to_trade4me(stopCopy,provider)
		print '%s %s' % (response['response'], provider)	
	
	saveEvents(removeList, 'REMOVE');
	
	#wait = raw_input("PRESS ENTER TO CONTINUE.")
			
def copyProviders():
	print "\n ##########################################################################################"
	print " Copy Providers"
	print " ##########################################################################################"
	#Copy providers
	for provider in addList.keys():
		try:
			response = post_to_trade4me(startCopy,r_subscribedRobots_username[provider])
		except KeyError:
			response = post_to_trade4me(startCopy,provider)
		print '%s %s for $%s' % (response['response'], provider, str(my_bet))
		
	saveEvents(addList, 'ADD');
	
	#wait = raw_input("PRESS ENTER TO CONTINUE.")
			

def printActiveList():
	print "\n ##########################################################################################"
	print " Active List"
	print " ##########################################################################################"
	position=0
	total_profit=0
	total_trades=0
	total_wins=0
	average_ratio=0
	average_slope=0
	t = PrettyTable(['Position', 'User_Name', 'Display_Name', 'Profit', 'Num_Trades', 'Win_Count', 'Win_Ratio', 'Sub_End'])
	for provider in sorted(rank, key=rank.get, reverse=True):
		if provider in activeRobots.values():
			position+=1
			diff_days_string =""
			if num_trades[provider] > 0:
				total_profit+=rank[provider]
				total_trades+=num_trades[provider]
				total_wins+=num_wins[provider]
				average_ratio+=ratio[provider]
				average_slope+=slope[provider]
			if provider in r_subscribedRobots.keys():
				diff=r_subscribedRobots[provider]-datetime.date.today()
				diff_days_string=diff.days				
			t.add_row([position, r_activeRobots[provider], provider, rank[provider], num_trades[provider], num_wins[provider], ratio[provider], diff_days_string])	
	total_profit=total_profit
	total_trades=total_trades
	total_wins=total_wins
	try:
		average_ratio=(float(total_wins)/float(total_trades))*100			
	except ZeroDivisionError:
		average_ratio=0
	average_slope=average_slope/position			
	t.add_row(['---', '---', '---', '---', '---', '---', '---', '---'])		
	t.add_row(['Net', '---', '---', total_profit, total_trades, total_wins, round(average_ratio,1), '---'])
	print t		
	
def printBestProviderList():
	print "\n ##########################################################################################"
	print " Best Provider List"
	print " ##########################################################################################"
	position=0
	total_profit=0
	total_trades=0
	total_wins=0
	average_ratio=0
	average_slope=0
	if len(bestProviders) > 0:
		t = PrettyTable(['Position','Status', 'User_Name', 'Profit', 'Num_Trades', 'Win_Count', 'Win_Ratio', 'Slope'])
		for provider in sorted(rank, key=rank.get, reverse=True):
			if provider in bestProviders:
				position+=1
				status_string=""
				if provider in r_activeRobots.keys():
					status_string+='A'
				if provider in r_subscribedRobots.keys():
					if len(status_string) > 0:
						status_string+=',S'
					else:
						status_string+='S'
					
				if num_trades[provider] > 0:
					total_profit+=rank[provider]
					total_trades+=num_trades[provider]
					total_wins+=num_wins[provider]
					average_slope+=slope[provider]
				
				t.add_row([position, status_string, provider, rank[provider], num_trades[provider], num_wins[provider], ratio[provider], slope[provider]])
										
		total_profit=total_profit
		total_trades=total_trades
		total_wins=total_wins
		try:
			average_ratio=(float(total_wins)/float(total_trades))*100			
		except ZeroDivisionError:
			average_ratio=0
		t.add_row(['---', '---', '---', '---', '---', '---', '---', '---'])		
		t.add_row(['Net', '---', '---', total_profit, total_trades, total_wins, round(average_ratio,1), round(average_slope,1)])
		print t		

def printCurrentTrades():
	print "\n ##########################################################################################"
	print " Current Trade List"
	print " ##########################################################################################"
	position=0
	total_profit=0
	total_trades=0
	total_wins=0
	average_ratio=0
	average_slope=0
	currentProviders={}
	t = PrettyTable(['Position', 'Status', 'User_Name', 'Profit', 'Num_Trades', 'Win_Count', 'Win_Ratio', 'Slope'])
	for provider in sorted(rank, key=rank.get, reverse=True):
		if rank[provider] != 0:
			position+=1
			status_string=""
			diff_days_string =""
			currentProviders[provider]=rank[provider]
			if provider in r_activeRobots.keys():
				status_string+='A'
			if provider in r_subscribedRobots.keys():
				if len(status_string) > 0:
					status_string+=',S'
				else:
					status_string+='S'
			t.add_row([position, status_string, provider, rank[provider], num_trades[provider], num_wins[provider], ratio[provider], slope[provider]])	
	f = open('currentProviders.txt','w')
	f.write(str(currentProviders))
	f.close()			
	#t.add_row(['---', '---', '---', '---', '---', '---', '---', '---'])		
	#t.add_row(['Net', '---', '---', total_profit, total_trades, round(average_ratio,1), round(average_slope,1)])
	print t		

def printHistoricTrades():
	print "\n ##########################################################################################"
	print " Trade History (%s)" % (my_robot_name)
	print " ##########################################################################################"
	position=0
	total_profit=0
	total_wins=0
	total_trades=0
	average_ratio=0
	t = PrettyTable(['Position', 'Status', 'Display_Name', 'Profit', 'Num_Trades', 'Win_Count', 'Win_Ratio'])
	for provider in sorted(h_rank, key=h_rank.get, reverse=True):
		if h_num_trades[provider] > 0 and provider not in [my_robot_name, new_robot_name]:
			position+=1
			total_profit+=h_rank[provider]
			total_trades+=h_num_trades[provider]			
			total_wins+=h_num_wins[provider]
			status_string=""
			if provider in r_activeRobots.keys():
				status_string+='A'
			if provider in r_subscribedRobots.keys():
				if len(status_string) > 0:
					status_string+=',S'
				else:
					status_string+='S'			
			t.add_row([position, status_string, provider, h_rank[provider], h_num_trades[provider], h_num_wins[provider], h_ratio[provider]])	
								
	total_profit=total_profit
	total_trades=total_trades
	total_wins=total_wins
	try:
		average_ratio=(float(total_wins)/float(total_trades))*100			
	except ZeroDivisionError:
		average_ratio=0
	t.add_row(['---', '---', '---', '---', '---', '---', '---'])		
	t.add_row(['Net', '---', '---', total_profit, total_trades, total_wins, round(average_ratio,1)])
	print t	
	
def printDeltaReport():
	print "\n ##########################################################################################"
	print " Delta Report"
	print " ##########################################################################################"
	position=0
	total_profit=0
	total_wins=0
	total_trades=0
	average_ratio=0
	t = PrettyTable(['Position', 'Status', 'Display_Name', 'Delta_Profit'])
	for provider in sorted(profit_delta, key=profit_delta.get, reverse=True):
		if profit_delta[provider] != 0:
			position+=1
			total_profit+=profit_delta[provider]
			status_string=""
			if provider in r_activeRobots.keys():
				status_string+='A'
			if provider in r_subscribedRobots.keys():
				if len(status_string) > 0:
					status_string+=',S'
				else:
					status_string+='S'			
			t.add_row([position, status_string, provider, profit_delta[provider]])	
							
	total_profit=total_profit
	print t		
	
def FixAddRemoveList():				
	D_addList=[]
	D_removeList=[]
	W_addList=[]
	W_removeList=[]
	d_provider_results={}
	d_history_results={}
	
	##Add providers to be activated from subscribed list
	for provider in bestProviders:
		if (provider in r_subscribedRobots.keys()):
			W_addList.append(provider)
	
	##Remove providers from activated list	
	for provider in sorted(h_rank, key=h_rank.get, reverse=True):
		if h_num_trades[provider] > 0 and provider not in [my_robot_name, new_robot_name]:	
			if (provider in r_subscribedRobots.keys()):				
				if ((h_num_trades[provider] >= 10) and (h_ratio[provider] < 58)):
					W_removeList.append(provider)
					while provider in W_addList:
						W_addList.remove(provider)
				elif ((h_num_trades[provider] >= 5) and (h_num_trades[provider] < 10) and (h_ratio[provider] < 55)):
					W_removeList.append(provider)
					while provider in W_addList:
						W_addList.remove(provider)
				elif ((h_num_trades[provider] < 5) and h_rank[provider] < -2*my_bet):
					W_removeList.append(provider)
					while provider in W_addList:
						W_addList.remove(provider)		
							
				#Turn on providers that were previously turned off and performing above 60		
				if h_num_trades[provider] >= 4 and h_ratio[provider] >= 60:
					if provider not in W_addList:
						W_addList.append(provider)
					while provider in W_removeList:
						W_removeList.remove(provider)	
		
	#Get today's rommjp Results
	sql="select a.provider, ROUND((SUM(a.win_count)/SUM(a.num_of_trades))*100,1) as win_ratio, SUM(a.num_of_trades) as total_num_of_trades, SUM(a.win_count) as total_win_cnt, SUM(a.win_count) * %d - %d * SUM(a.num_of_trades) as profit_5 from trade_analysis a where a.close_date = '%s' \
		  group by a.provider \
		  order by profit_5 desc"%(returns[my_bet], my_bet, gmt_date)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		if row[0]:
			provider=row[0]
			win_ratio=float(row[1])
			total_num_of_trades=int(row[2])
			total_win_cnt=int(row[3])
			profit=float(row[4])
			d_provider_results[provider]=[profit,win_ratio]
			
			##Remove providers from activated list		
			if provider in r_subscribedRobots.keys():							
				#Turn on providers that were previously turned off and performing above 59		
				if total_num_of_trades >= 4 and win_ratio > 58:
					if provider not in D_addList:
						D_addList.append(provider)
					while provider in D_removeList:
						D_removeList.remove(provider)							
	
	#Remove today's rommbot performance							
	sql="select a.provider, ROUND((SUM(a.win_count)/SUM(a.num_of_trades))*100,1) as win_ratio, SUM(a.num_of_trades) as total_num_of_trades, SUM(a.win_count) as total_win_cnt, SUM(a.win_count) * %d - %d * SUM(a.num_of_trades) as profit_5 from rommbot_analysis a where a.close_date = '%s' \
		  group by a.provider \
		  order by profit_5 desc"%(returns[my_bet], my_bet, gmt_date)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		if row[0]:
			provider=row[0]
			win_ratio=float(row[1])
			total_num_of_trades=int(row[2])
			total_win_cnt=int(row[3])
			profit=float(row[4])
			d_history_results[provider]=[profit,win_ratio]
			
			#print provider, total_num_of_trades, total_win_cnt, win_ratio
			
			##Remove providers from activated list		
			if provider in r_subscribedRobots.keys():
				if ((total_num_of_trades >= 10) and (win_ratio < 58)):
					D_removeList.append(provider)
					while provider in D_addList:
						D_addList.remove(provider)
				elif ((total_num_of_trades >= 5) and (total_num_of_trades < 10) and (win_ratio < 55)):
					D_removeList.append(provider)
					while provider in D_addList:
						D_addList.remove(provider)
				elif ((total_num_of_trades < 5) and profit < -2*my_bet):
					D_removeList.append(provider)
					while provider in D_addList:
						D_addList.remove(provider)		
						
				#Turn on providers that were previously turned off and performing above 60		
				if total_num_of_trades >= 4 and win_ratio >= 60:
					if provider not in D_addList:
						D_addList.append(provider)
					while provider in D_removeList:
						D_removeList.remove(provider)							


	sql="select e.providers, e.`action`, e.datetime_stamp, e.comments from event_tracker e where e.datetime_stamp  like '%s' order by e.datetime_stamp desc" % ('%'+strftime("%Y-%m-%d", gmtime())+'%')
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		providers={}
		p_array={}
		provider = row[0]
		action = row[1]
		datetime_stamp = row[2]
		comments = row[3]
		comments_array = comments.split(';')
		p_array = provider.split(';')
		
		for idx, provider in enumerate(p_array):
			if comments_array[idx].split(' ')[0]=='Daily':
				#print provider, action, datetime_stamp, comments
				if action == 'ADD':
					providers = event_data['Daily']['ADD']
					if provider not in providers:
						providers[provider]=datetime_stamp
					else:
						if datetime_stamp > providers[provider]:
							providers[provider]=datetime_stamp
					event_data['Daily']['ADD']=providers
				elif action == 'REMOVE':
					providers = event_data['Daily']['REMOVE']
					if provider not in providers:
						providers[provider]=datetime_stamp
					else:
						if datetime_stamp > providers[provider]:
							providers[provider]=datetime_stamp
					event_data['Daily']['REMOVE']=providers		
			else:
				if action == 'ADD':
					providers = event_data['Weekly']['ADD']
					if provider not in providers:
						providers[provider]=datetime_stamp
					else:
						if datetime_stamp > providers[provider]:
							providers[provider]=datetime_stamp
					event_data['Weekly']['ADD']=providers
				elif action == 'REMOVE':
					providers = event_data['Weekly']['REMOVE']
					if provider not in providers:
						providers[provider]=datetime_stamp
					else:
						if datetime_stamp > providers[provider]:
							providers[provider]=datetime_stamp
					event_data['Weekly']['REMOVE']=providers	

	print "\nbestProviders: "+str(bestProviders)					
	print "D_addList: "+str(D_addList)
	print "D_removeList: "+str(D_removeList)
	print "W_addList: "+str(W_addList)
	print "W_removeList: "+str(W_removeList)
	
	#Add bots who are earning profit today
	for bot in D_addList:
		if bot not in r_activeRobots.keys(): 
			addList[bot]='Daily Add'
	
	#Remove bots who are not earning profit today	
	for bot in D_removeList:
		if bot in d_provider_results.keys() and bot in d_history_results.keys():
			if bot in r_activeRobots.keys():
				if ((d_provider_results[bot][0]-d_history_results[bot][0]>0) and (d_provider_results[bot][1] >= 58)):
					continue
				else:
					removeList[bot]='Daily Remove %s %% %s'%(bot, d_provider_results[bot][1])	
			else:
				if ((d_provider_results[bot][0]-d_history_results[bot][0]>0) and (d_provider_results[bot][1] >= 58)):
					addList[bot]='Daily Add %s %% %s'%(bot, d_provider_results[bot][1])	
	
	#Add bots who are earning profit this week
	for bot in W_addList:
		if bot in D_removeList:
			while bot in addList.keys():
				del addList[bot]
		else:
			if bot not in r_activeRobots.keys():
				addList[bot]='Weekly Add Best Providers'			

	#Remove bots who are not earning this week	
	for bot in W_removeList:
		if bot in D_addList:
			while bot in removeList.keys():
				del removeList[bot]
		else:
			if bot in rank.keys() and bot in h_rank.keys():
				if bot in r_activeRobots.keys():
					if ((rank[bot]-h_rank[bot]>0) and (ratio[bot] >= 58)):			
						continue
					else:
						if bot in event_data['Daily']['ADD'].keys(): #Ignore Weekly REMOVE if there is a DAILY ADD today
							continue
						else:
							removeList[bot]='Weekly Remove %s %% %s'%(bot, ratio[bot])
				else:
					if ((rank[bot]-h_rank[bot]>0) and (ratio[bot] >= 58)):	
						if bot in event_data['Daily']['REMOVE'].keys(): #Ignore Weekly ADD if there is a DAILY REMOVE today
							continue
						else:					
							addList[bot]='Weekly Add %s %% %s'%(bot, ratio[bot])	
							
	'''
	#Providers showing a signigificant profit delta should be added				
	for bot in sorted(profit_delta, key=profit_delta.get, reverse=True):
		if bot in r_subscribedRobots.keys():
			if profit_delta[bot] > (returns[my_bet]-my_bet):
				#print bot, profit_delta[bot]
				if bot not in r_activeRobots.keys():
					addList[bot]='Add by Profit Delta %s'%(str(profit_delta[bot]))
				while bot in removeList.keys():
					del removeList[bot]
			elif profit_delta[bot] < -2*my_bet:			
				if bot in r_activeRobots.keys():
					removeList[bot]='Remove by Profit Delta %s'%(str(profit_delta[bot]))
				while bot in addList.keys():
					del addList[bot]
	'''

def FixAddRemoveList2():						
	W_addList=[]
	W_removeList=[]
	
	print "\nbestProviders: "+str(bestProviders)
	
	##Add providers to be activated from subscribed list
	for provider in bestProviders:
		if (provider in r_subscribedRobots.keys()):
			W_addList.append(provider)
	
	##Remove providers from activated list	
	for provider in sorted(h_rank, key=h_rank.get, reverse=True):
		if h_num_trades[provider] > 0 and provider not in [my_robot_name, new_robot_name]:	
			if (provider in r_subscribedRobots.keys()):				
				if ((h_num_trades[provider] >= 10) and (h_ratio[provider] < 56)):
					W_removeList.append(provider)
					while provider in W_addList:
						W_addList.remove(provider)
				elif ((h_num_trades[provider] >= 5) and (h_num_trades[provider] < 10) and (h_ratio[provider] < 45)):
					W_removeList.append(provider)
					while provider in W_addList:
						W_addList.remove(provider)
				elif ((h_num_trades[provider] < 5) and h_rank[provider] < -2*my_bet):
					W_removeList.append(provider)
					while provider in W_addList:
						W_addList.remove(provider)		
							
				#Turn on providers that were previously turned off and performing above 56		
				if h_num_trades[provider] >= 1 and h_ratio[provider] > 56:
					if provider not in W_addList:
						W_addList.append(provider)
					while provider in W_removeList:
						W_removeList.remove(provider)	
		
	print "W_addList: "+str(W_addList)
	print "W_removeList: "+str(W_removeList)
						
	#Add bots who are earning profit this week
	for bot in W_addList:
		if bot not in r_activeRobots.keys():
			addList[bot]='Weekly Add Best Provider'
	
	#Remove bots who are not earning this week	
	for bot in W_removeList:
		if bot in rank.keys() and bot in h_rank.keys():
			if bot in r_activeRobots.keys():
				if ((rank[bot]-h_rank[bot]>0) and (ratio[bot] > 55)):
					continue	
				else:
					removeList[bot]='Weekly Remove %s %% %s'%(bot, ratio[bot])
					
			else:
				if ((rank[bot]-h_rank[bot]>0) and (ratio[bot] > 55)):			
					addList[bot]='Weekly Add %s %% %s'%(bot, ratio[bot])
'''
	#Add and remove robots that experienced large deltas				
	for bot in sorted(profit_delta, key=profit_delta.get, reverse=True):
		if bot in r_subscribedRobots.keys():
			if profit_delta[bot] > (returns[my_bet]-my_bet):
				#print bot, profit_delta[bot]
				if bot not in r_activeRobots.keys():
					if bot not in addList.keys():
						addList[bot]='Adding by Profit Delta %s'%(str(profit_delta[bot]))
				while bot in removeList.keys():
					del removeList[bot]
			elif profit_delta[bot] < -2*(returns[my_bet]-my_bet):			
				if bot in r_activeRobots.keys():
					if bot not in removeList.keys():
						removeList[bot]='Remove by Profit Delta %s'%(str(profit_delta[bot]))
				while bot in addList.keys():
					del addList[bot]	
'''			
	
def getProfitDelta():
	f = open('currentProviders.txt', 'r')
	getLine=False
	bannerCnt=0
	position=""
	provider=""
	profit=0
	getHistoricalProviderProfit={}
	for line in f:
		getHistoricalProviderProfit=ast.literal_eval(line)
		
	for provider in getHistoricalProviderProfit.keys():
		try:
			profit_delta[provider]=rank[provider]-getHistoricalProviderProfit[provider]
		except KeyError:
			profit_delta[provider]=0
					
	f.close()
	
#Start Main program	
print "GMT: "+ strftime("%a, %d %b %Y %H:%M:%S", gmtime())
#print "GMT: "+ strftime("%Y-%m-%d", gmtime())
print "Start date: "+ start_date.strftime("%a, %d %b %Y %H:%M:%S")
if datetime.datetime.utcnow().weekday() in range(0,5):
	activeRobots = get_from_trade4me(getActiveCopy)	
	subscribedRobots = get_from_trade4me(getSubscriptions)
	#getLastTrades(trade_window)
	getRobotData()
	getHistory()
	getRobotTrace()
	for bot in activeRobots:
		r_activeRobots[activeRobots[bot]]=bot
	for bot in subscribedRobots:
		date_string=subscribedRobots[bot]['end'].replace('\\','')
		date_array=date_string.split('/')
		end_date = datetime.date(int('20'+str(date_array[2])), int(date_array[1]), int(date_array[0]))
		r_subscribedRobots[subscribedRobots[bot]['display_name']]=end_date
		r_subscribedRobots_username[subscribedRobots[bot]['display_name']]=bot
	print "Total Robot Count: "+str(len(results.keys()))
	getRank()
	getSlope()
	getBestProviders()
	getProfitDelta()
	printCurrentTrades()
	printBestProviderList()
	printHistoricTrades()
	#printActiveList()
	printDeltaReport()
	FixAddRemoveList()
	print "\n ##################################"	
	printMonthlyReport([new_robot_name])
	printMonthlyReport([my_robot_name])
	if len(removeList.keys()) > 0:
		print "\nCurrent Providers to be REMOVED: %s " % (str(removeList.keys()))
		stopProviders()
	if len(addList.keys()) > 0:
		print "\nCurrent Providers to be ADDED: %s " % (str(addList.keys()))
		copyProviders()
	
	#RUN SIKULI SCRIPT TO REFRESH PROVIDER SELECTION
	os.system("C:\\Users\\rommj\\Documents\\runsikulix.cmd -r C:\\Users\\rommj\\Documents\\workspace\\binary_bot\\refresh.sikuli")
	
	#plotRobots()
else:
	print "rommbot is OFFLINE: Currently not in GMT trading times"		

cur.close()
SQL_db.close()	
