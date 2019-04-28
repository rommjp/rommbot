'''
Created 30/10/2017 -- R.Poggenberg 
'''

import os
import MySQLdb
import xlrd
import datetime
import urllib2
from pprint import pprint
from time import gmtime, strftime

rommjp_data={}
new_robot_name='Target_A'
my_robot_name='rommbot'
path= 'C:\\Users\\rommj\\Downloads'
start_date_string = strftime("%Y-%m-%d", gmtime())
#start_date_string = str(datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())) #Use Current Monday of the week as startime
start_date = datetime.datetime.strptime(start_date_string, '%Y-%m-%d')
spreadsheets=[]
my_bet=5
returns = {1:1.8,5:9,7:13,10:18,20:36,25:45,35:63,40:72,50:91,75:135,100:182,150:273,175:319,200:370,250:455,275:500,300:545,500:917}
SQL_db = MySQLdb.connect(host="localhost", user="root",passwd="gamboa85", db="binary_data") # name of the data base
cur = SQL_db.cursor()
print "GMT: "+ strftime("%a, %d %b %Y %H:%M:%S", gmtime())
print "Startdate: %s" % (start_date_string)

if datetime.datetime.utcnow().weekday() in range(0,5):
	#REMOVE CURRENT Trading_history files in download folder
	file_paths = os.listdir(path)
	for filename in file_paths:
		if "Trading_history" in filename:
			if os.path.exists(path+"\\"+filename):
				print "REMOVED %s" % (filename)
				os.remove(path+"\\"+filename)
			else:
				print "FILE %s DOESN'T EXIST" % (filename)

	#RUN SIKULI SCRIPT TO AUTOMATE DOWNLOAD OF FILES
	os.system("C:\\Users\\rommj\\Documents\\runsikulix.cmd -r C:\\Users\\rommj\\Documents\\workspace\\binary_bot\\binary_bot.sikuli")
	
	#REMOVE CURRENT TRADING DATA FROM START DATE SPECIFIED	
	sql="select count(*) FROM trade_history WHERE close_date >= '%s'" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		if int(row[0]) > 0:
			print "-- DELETED trade_history providers data from date '%s'"%(start_date_string)
			sql="DELETE FROM trade_history WHERE close_date >= '%s'" % (start_date_string)
			cur.execute(sql)
			SQL_db.commit()	
			
			
	sql="select count(*) FROM trade_analysis WHERE close_date >= '%s'" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		if int(row[0]) > 0:
			print "-- DELETED trade_analysis providers data from date '%s'"%(start_date_string)
			sql="DELETE FROM trade_analysis WHERE close_date >= '%s'" % (start_date_string)
			cur.execute(sql)
			SQL_db.commit()			
					
	sql="select count(*) FROM rommbot_analysis WHERE close_date >= '%s'" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		if int(row[0]) > 0:
			print "-- DELETED rommbot_analysis providers data from date '%s'"%(start_date_string)
			sql="DELETE FROM rommbot_analysis WHERE close_date >= '%s'" % (start_date_string)
			cur.execute(sql)
			SQL_db.commit()				
			
			
	sql="select count(*) FROM trade_history_new WHERE close_date >= '%s'" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		if int(row[0]) > 0:
			print "-- DELETED trade_history_new providers data from date '%s'"%(start_date_string)
			sql="DELETE FROM trade_history_new WHERE close_date >= '%s'" % (start_date_string)
			cur.execute(sql)
			SQL_db.commit()				
	
	#INSERT NEW TRADING DATA BASED ON NEW INFO		
	spreadsheets=['Trading_history_with_tabs','Trading_history_with_tabs (1)', 'Trading_history_with_tabs (2)', 'Trading_history_with_tabs (3)', 'Trading_history (1)', 'Trading_history']
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
			for rownum in range(sh.nrows):			
				if rownum > 0:
					row = sh.row_values(rownum)
					if row[7] != 'pending':
						s_asset=row[1]
						s_open_date=str(datetime.datetime(*xlrd.xldate_as_tuple(row[2], wb.datemode)))
						s_open_price=row[3]
						s_direction=row[4]
						s_close_price=row[6]
						s_close_date=str(datetime.datetime(*xlrd.xldate_as_tuple(row[5], wb.datemode)))
						win_loss = 1 if row[7] == 'won' else 0 if row[7] =='loss' else 0 #determine win loss value
						s_source = row[10]
						s_date = s_close_date.split(' ')[0]
						s_time = s_close_date.split(' ')[1]	
						if datetime.datetime.strptime(s_date, '%Y-%m-%d') >= start_date:			
							sql = "INSERT INTO trade_history (provider, asset, open_date, open_price, direction, close_date, close_price, win_loss, source)\
									VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s')" % (robot_s, s_asset, s_open_date, s_open_price, s_direction, s_close_date, s_close_price, win_loss, s_source)
							print sql		
							cur.execute(sql)
							SQL_db.commit()		

	sql = "select distinct t.provider from trade_history t WHERE t.close_date >= '%s' order by t.provider" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	providers=[]
	for row in results:
		providers.append(row[0])
			
	for robot in providers:
		datetime_array=[]
		win_ratio_array=[]
		daily_trades_array=[]
		highcharts_data=[]
		sql="select t1.provider, SUBSTRING_INDEX(t1.close_date,' ',1) as final_close_date, t2.win_loss_count, count(t1.ID) as total_trades, ROUND((t2.win_loss_count / count(t1.ID))*100,1) as win_ratio  from trade_history t1 \
			inner join \
			( \
			select t.provider,SUBSTRING_INDEX(t.close_date,' ',1) as close_date, t.win_loss, count(t.win_loss) as win_loss_count from trade_history t where t.provider='%s' and t.win_loss=1 and t.close_date >= '%s'\
			group by SUBSTRING_INDEX(t.close_date,' ',1), t.win_loss \
			) t2 on (SUBSTRING_INDEX(t1.close_date,' ',1)=t2.close_date and t1.provider=t2.provider) \
			where t1.provider='%s'\
			group by SUBSTRING_INDEX(t1.close_date,' ',1) \
			order by SUBSTRING_INDEX(t1.close_date,' ',1) " % (robot, start_date_string, robot)
		cur.execute(sql)
		results2 = cur.fetchall()
		for row2 in results2:
			#print row2[0], row2[1], row2[2], row2[3], row2[4]
			provider=row2[0]
			final_close_date=row2[1]
			win_count=int(row2[2])
			total_trades=int(row2[3])
			win_ratio=float(row2[4])	
			profit = (win_count*returns[my_bet])-(my_bet*total_trades)
			if provider not in ['rommjp']:
				sql="INSERT INTO trade_analysis (provider, close_date, profit, num_of_trades, win_count, win_ratio) \
					VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (provider, datetime.datetime.strptime(final_close_date, "%Y-%m-%d"), profit, total_trades, win_count, win_ratio)
				print sql		
				cur.execute(sql)
				SQL_db.commit()
			
	sql="select SUBSTRING_INDEX(t.close_date,' ',1) as close_date ,t.source as provider, 9*SUM(t.win_loss) - 5*COUNT(t.win_loss) as 5_profit, COUNT(t.win_loss) as num_trades, SUM(t.win_loss)  as win_count, ROUND((SUM(t.win_loss)/COUNT(t.win_loss))*100,1) as win_ratio from trade_history t where t.provider = 'rommbot' and t.close_date >= '%s' \
		group by SUBSTRING_INDEX(t.close_date,' ',1), t.source \
		order by t.close_date asc" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		close_date=row[0]
		provider=row[1].split('Copied from ')[1]
		profit=row[2]
		total_trades=row[3]
		win_count=row[4]
		win_ratio=row[5]
		sql="INSERT INTO rommbot_analysis (provider, close_date, profit, num_of_trades, win_count, win_ratio) \
			VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (provider, datetime.datetime.strptime(close_date, "%Y-%m-%d"), profit, total_trades, win_count, win_ratio)
		print sql		
		cur.execute(sql)
		SQL_db.commit()	
		
	sql="select SUBSTRING_INDEX(t.close_date,' ',1) as close_date ,t.source as provider, 9*SUM(t.win_loss) - 5*COUNT(t.win_loss) as 5_profit, COUNT(t.win_loss) as num_trades, SUM(t.win_loss)  as win_count, ROUND((SUM(t.win_loss)/COUNT(t.win_loss))*100,1) as win_ratio from trade_history t where t.provider = 'rommjp' and t.close_date >= '%s' \
		group by SUBSTRING_INDEX(t.close_date,' ',1), t.source \
		order by t.close_date asc" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		close_date=row[0]
		provider=row[1].split('Copied from ')[1]
		profit=row[2]
		total_trades=row[3]
		win_count=row[4]
		win_ratio=row[5]
		if close_date in rommjp_data.keys():
			if provider not in rommjp_data[close_date].keys():
				rommjp_data[close_date][provider]=[profit, total_trades, win_count, win_ratio]				
		else:
			rommjp_data[close_date]={}
			rommjp_data[close_date][provider]=[profit, total_trades, win_count, win_ratio]
	
	for close_date in rommjp_data.keys():
		for provider in rommjp_data[close_date]:
			print "-- DELETED trade_analysis providers data from date '%s' and provider is '%s'"%(start_date_string, provider)
			sql="DELETE FROM trade_analysis WHERE close_date = '%s' and provider = '%s' " % (close_date, provider)
			cur.execute(sql)
			SQL_db.commit()					
			profit = rommjp_data[close_date][provider][0]
			total_trades = rommjp_data[close_date][provider][1]
			win_count = rommjp_data[close_date][provider][2]
			win_ratio = rommjp_data[close_date][provider][3]
			sql="INSERT INTO trade_analysis (provider, close_date, profit, num_of_trades, win_count, win_ratio) \
				VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (provider, datetime.datetime.strptime(close_date, "%Y-%m-%d"), profit, total_trades, win_count, win_ratio)
			print sql		
			cur.execute(sql)
			SQL_db.commit()		
			
	sql = "select t.* from trade_history t where t.close_date > '%s' and t.provider='rommjp' order by t.source, t.close_date desc" % (start_date_string)
	cur.execute(sql)
	results = cur.fetchall()
	for row in results:
		#print row
		ID = 		 row[0]
		provider = 	 row[1]
		asset = 	 row[2]
		open_date =  row[3]
		open_price = row[4]
		direction =  row[5]
		close_date = row[6]
		close_price =row[7]
		win_loss =   ord(row[8])
		source =     row[9].split('Copied from ')[1]
		#print ID,provider,asset,open_date,open_price,direction,close_date,close_price,win_loss,source
		
		sql="INSERT INTO trade_history_new (provider, asset, open_date, open_price, direction, close_date,close_price,win_loss) \
			VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (source,asset,open_date,open_price,direction,close_date,close_price,win_loss)
		print sql		
		cur.execute(sql)
		SQL_db.commit()		

	sql="insert into trade_history_new (provider, asset, open_date, direction, close_date, close_price, win_loss) \
		select t.provider, t.asset, t.open_date, t.direction, t.close_date, t.close_price, t.win_loss from trade_history t where t.provider='rommbot' and t.close_date >= '%s' order by t.close_date desc" %(start_date_string)	
	print sql		
	cur.execute(sql)
	SQL_db.commit()			
			
else:
	print "rommbot is OFFLINE: Currently not in GMT trading times"			
	
cur.close()
SQL_db.close()		
