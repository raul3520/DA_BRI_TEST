import mysql.connector
from mysql.connector import Error
import sys
import csv
import os.path
from os import path
import datetime
def doc():
    '''Usage syntax is python scriptnmame dbupdater
	python scriptnmame report Corona/k8s Day/Week
	python scriptnmame status'''
if len(sys.argv) <= 1 or sys.argv[1] == "-h":
    print(doc.__doc__)    
    sys.exit(1)

f = open("file.txt")
f.seek(0)
fulldict={}
dblist = []
for db in f.readlines():
    dblist.append(db.rstrip('\n').split(','))
    #print(dblist)
[fulldict.update({i[0]:i[1::]}) for i in dblist]
def statuscheck():
    status = {}
    for each in dblist:
	response = os.system("ping -c 1 " + each[1])
	print(response)
	if response == 0:
	    pingstatus = "Network Active"
	else:
    	    pingstatus = "Network Error"
	    status[each[0]]="Network Error"
	    continue
        try:
            connection = mysql.connector.connect(host=each[1],
                                                 user=each[2],
                                                 password=each[3])
            if connection.is_connected():
                #db_Info = connection.get_server_info()
                # print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("show databases")
                record = cursor.fetchone()
                status[each[0]] = "Up and Running"
        except Error as e:
#            print("Error while connecting to MySQL ", each[0], e)
            status[each[0]] = str(e)
    print("#############################################")
    print(status)
    print("#############################################")

def dbupdater():
#    inp=raw_input("The supported feature are csv data updare for Cdata and Salesreport ,Please copy the csv record in the format cdata.csv or Salesreport.csv.If you wish to run custom query then select 1 else type 0 : ")
    inp=sys.argv[2]
    print(inp)
    if inp == "default":
	print("you optd to load from csv")
	if path.exists("cdata.csv"):
	    print("Cdata.csv exist")
	    with open('cdata.csv', mode='r') as csv_data:
	        reader = csv.reader(csv_data, delimiter=',')
                csv_data_list = list(reader)
            connection = mysql.connector.connect(host=fulldict.get('dbinstance2')[0],
                                                 user=fulldict.get('dbinstance2')[1],
                                                 password=fulldict.get('dbinstance2')[2],
						 database="Cdata")
 	    

            cursor = connection.cursor()
	    for row in csv_data_list:
		cursor.execute("insert into CoronaData(date,cases,deaths,countriesAndTerritories) values(%s,%s,%s,%s)",(row[0],row[1],row[2],row[3]))
	    print("Cdata uploaded")
    	    connection.commit()
            cursor.close()
            connection.close()
	    del csv_data_list
	else:
	    print("Cdata not found")
	if path.exists("Salesreport.csv"):
	    print("Salesreport.csv exist")
	    with open('Salesreport.csv', mode='r') as csv_data:
                reader = csv.reader(csv_data, delimiter=',')
                csv_data_list = list(reader)
	        connection = mysql.connector.connect(host=fulldict.get('dbinstance1')[0],
                                                 user=fulldict.get('dbinstance1')[1],
                                                 password=fulldict.get('dbinstance1')[2],
                                                 database="sales")
		cursor = connection.cursor()
		for row in csv_data_list:
                    cursor.execute("insert into salesreport(Itemtype,TotalRevenue,TotalProfit) values(%s,%s,%s)",(row[0],row[1],row[2]))
            	print("Sales report uploaded successfully")
		connection.commit()
            	cursor.close()
            	connection.close()
	else:
	    print("Sales data not found")
    elif inp == "custom":
	print(fulldict.keys())
	inp=raw_input("Enter the dbinstancename from above list : ")
	query=raw_input("Enter the query : ")
	print(query) 
        connection = mysql.connector.connect(host=fulldict.get(inp)[0],
                                                 user=fulldict.get(inp)[1],
                                                 password=fulldict.get(inp)[2]) 
	cursor = connection.cursor()
	cursor.execute(query)
	record = cursor.fetchall()
	print(record)
	
    else:
	print("Wrong input")

def report():
    dt=datetime.datetime.now()
    dtnow=dt.strftime("%Y-%m-%d")
    #inp=raw_input("Supported report are K8s and Corona, Select one among it :")
    if sys.argv[2] == "k8s":
	connection = mysql.connector.connect(host=fulldict.get('dbinstance1')[0],
                                                 user=fulldict.get('dbinstance1')[1],
                                                 password=fulldict.get('dbinstance1')[2],
                                                 database="k8s")
	cursor = connection.cursor()
	if sys.argv[3] == "Day":
            print("You have selected day report")
            cursor = connection.cursor()
            query="select * from stats where Time like '"+dtnow+"%'"
            cursor.execute(query)
            result=cursor.fetchall()
            with open(dtnow+'k8s.csv','w') as file:
                writer = csv.writer(file)
                for row in result:
                    #print(row)
                    writer.writerow(row)
	    print("Report is stored in"+dtnow+"k8s.csv")
        elif sys.argv[3] == "Week":
            print("You have selected week report")
            query="select * from stats where Time >= DATE(NOW()) - INTERVAL 7 DAY"
            cursor.execute(query)
            result=cursor.fetchall()
            with open('7daysdata_k8s.csv','w') as file:
                writer = csv.writer(file)
                for row in result:
                    #print(row)
                    writer.writerow(row)
	    print("Report is stored in  7daysdata_k8s.csv")
        else:
            print("Not valid Input")
 
    elif sys.argv[2] == "Corona":
        connection = mysql.connector.connect(host=fulldict.get('dbinstance2')[0],
                                                 user=fulldict.get('dbinstance2')[1],
                                                 password=fulldict.get('dbinstance2')[2],
                                                 database="Cdata")
	cursor = connection.cursor()
#	inp1=raw_input("Day report or week report ,Enter input as Day/Week")
	if sys.argv[3] == "Day":
	    print("You have selected day report")
            cursor = connection.cursor()
	    query="select countriesAndTerritories,cases,deaths from CoronaData where date like '"+dtnow+"'"
	    cursor.execute(query)
            result=cursor.fetchall()
	    with open(dtnow+'.csv','w') as file:
		writer = csv.writer(file)
         	for row in result:
        	    #print(row)
                    writer.writerow(row)
	    print("Report is saved in "+dtnow+".csv")
	elif sys.argv[3] == "Week":
	    print("You have selected week report")
	    query="select * from CoronaData where date >= DATE(NOW()) - INTERVAL 7 DAY"
	    cursor.execute(query)
            result=cursor.fetchall()
            with open('7daysdata.csv','w') as file:
                writer = csv.writer(file)
                for row in result:
                    #print(row)
                    writer.writerow(row)
	    print("Report is stored in  7daysdata.csv")
	else:
	    print("Not valid Input")
	    
if sys.argv[1] == "statuscheck":
    statuscheck()
elif sys.argv[1] == "dbupdater":
    dbupdater()
elif sys.argv[1] == "report":
    report()
else:
    print(doc.__doc__) 
