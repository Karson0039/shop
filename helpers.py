import glob, os
import numpy as np
import sys
import csv
import random
from datetime import datetime

dataPath="Data"
cashierFee=0.25 #Cost per min of a cashier

itemRange = [[0,9], [10,14], [15,19], [20,30], [31,40],[41,1000]] #Holds the ranges in which items are divided

#Data handling files
#-----------------------------------------------------------------------------------------
def toSeconds(time):
	if(time=='0'):
		return 0
	times=time.split(":")
	return (int(times[0])*60)+int(times[1].split(".")[0])

def getData():
    Queues = {}
    os.chdir("/Users/user/Data")
    for file in glob.glob("*.csv"):
        with open(file) as csvfile:
            data = csv.reader(csvfile, delimiter=',')
            next(data, None)
            arrival = []
            serviceStart = []
            serviceEnd = []  # Fix the variable name here
            droptime = []
            items = []
            card = []
            waitTime = []
            serviceTime = []
            for row in data:
                arrival.append(row[1])
                serviceStart.append(row[2])
                serviceEnd.append(row[3])
                droptime.append(row[6])
                items.append(row[7])
                card.append(row[8])
                waitTime.append(toSeconds(row[4]) if row[4] else 0)  # Check for empty string
                serviceTime.append(toSeconds(row[5]) if row[5] else 0)
            Queues[file] = (arrival, serviceStart, serviceEnd, droptime, items, card, waitTime, serviceTime)
    return Queues

def getElapsed(time1,time2):
	elapsed = datetime.strptime(time2, '%H:%M:%S') - datetime.strptime(time1, '%H:%M:%S')
	return elapsed.total_seconds()


#Basic Calculations
#-----------------------------------------------------------------------------------------
def getArrivalRate(queue):
	arrivals=queue[0]
	interArrivalTime=[]
	for i in range(1,len(arrivals)):
			interArrivalTime.append(getElapsed(arrivals[i-1],arrivals[i]))
	return 1/(np.mean(interArrivalTime)/60)

def getServiceRate(queue):
	time=queue[7]
	return 1/(np.mean(time)/60)

def getWaitTime(queue):
	time=queue[6]
	return np.mean(time)/60

def getServiceUtil(arrival,service):
	return arrival/service

#Gets the number of items in a simulated queue
def numItems(queue):
	items=0
	for customer in queue:
		items+=customer['items']
	return items
#-----------------------------------------------------------------------------------------

def getProbs(items): #takes in the array of num of items
	ranges = []
	for j in range(len(itemRange)): ranges.append(0)
	prob = []
	total = len(items)

	for k in range(len(items)): #gets rids of drop outs that was counted
		if items[k]==0:
			total -= 1

	for i in range(len(items)):
		for j in range(len(ranges)):
			if int(items[i]) >= itemRange[j][0] and int(items[i]) <= itemRange[j][1]:
				ranges[j] += 1
				#break

	total = float(total)
	for j in range(len(ranges)):
		prob.append(ranges[j]/total)

	return prob

# Accepts the queue and returns the time difference as a tuple the first value is for cash, second for card
def TimeDifference(queue):
	location = -1
	card = queue[5]
	service = queue[7]

	# Given you use a card/cash whats your average service time
	avgCard = []
	avgCash = []

	for truth in card:
		location += 1
		if truth == '1':
			avgCard.append(service[location])
		else:
			avgCash.append(service[location])
	avgCard = np.mean(avgCard)
	avgCash = np.mean(avgCash)
	
	if (avgCash > avgCard):
		return ( 1 / abs(avgCash-avgCard) / 60,0)

	return (0, 1 / abs(avgCash-avgCard) / 60)

def averageServiceTime(queue):
	item_ranges = []
	service_time_ranges = []
	average_service_time_ranges = []
	for i in range(len(itemRange)):
		item_ranges.append(0)
		service_time_ranges.append([])
		average_service_time_ranges.append(0)
	
	items = queue[4]
	service_rates = queue[7]
	#print queue
	for i in range(len(items)):
		current_items = items[i]
		current_service_rate = service_rates[i]

		for j in range(len(itemRange)):
			if int(items[i]) >= itemRange[j][0] and int(items[i]) <= itemRange[j][1]:
				item_ranges[j] += 1
				service_time_ranges[j].append(current_service_rate)

	for i in range(len(item_ranges)):
		if(len(service_time_ranges[i]) > 0):
			average_service_time_ranges[i] = np.mean(service_time_ranges[i])
		else: average_service_time_ranges[i] = 0

	print(item_ranges)
	print(service_time_ranges)
	print(average_service_time_ranges) 

def main():
    Queues = getData()
    for queue in Queues:
        print(queue)

        arr = getArrivalRate(Queues[queue])
        ser = getServiceRate(Queues[queue])
        wait = getWaitTime(Queues[queue])
        prob = getProbs(Queues[queue][4])
        timeDifference = TimeDifference(Queues[queue])

        print("Arrival Rate ", arr)
        print("Service Rate ", ser)
        print("Wait Time ", wait)
        print("Service Utilization ", getServiceUtil(arr, ser))
        print("Time Difference", timeDifference, '\n')

        averageServiceTime(Queues[queue])


if __name__ == "__main__":
    main()


