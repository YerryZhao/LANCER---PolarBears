import csv 

device_name = "DICE"
date = "202318"

file = "./" + device_name + "_" + date + ".csv"

TimeStamps = []
Mac_Add = []
uMac_Add = []
aMac_Add = []
Start_Times = []
End_Times = []

with open(file, "r") as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    for row in csvreader: 
        if row[2] not in TimeStamps:
            TimeStamps.append(row[2])   # Finding Unique TimeStamps

    csvfile.seek(0)
    next(csvreader)

    for object in TimeStamps:
        list = [] 
        csvfile.seek(0)
        next(csvreader)
        for row in csvreader:
            if row[2] == object:
                list.append(row[4])
        Mac_Add.append(list)            # Finding All Mac Addresses sorted by TimeStamps

    #All Unique Mac Addresses
    for i in range(1, len(TimeStamps)):
        for address in Mac_Add[i]:
            if address not in aMac_Add: 
                aMac_Add.append(address)


def unique_add(Start, End):
    # finding unique Mac Ids

    with open(file, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)

        Start = "1673157599"
        End = "1673157992"

        for i in range(1, len(TimeStamps)):
            if TimeStamps[i] == Start:
                index_start = i
            elif TimeStamps[i] == End:
                index_end = i

        for i in range(index_start, index_end):
            for address in Mac_Add[i]:
                if address not in uMac_Add: 
                    uMac_Add.append(address)

        print(uMac_Add)

def Add_times(address): 
    # Finding Time Intervals of an address being at a location 

    start_time = "0"
    for i in range(0, len(TimeStamps)):

        if address in Mac_Add[i]:
            is_there = True
            if start_time == "0":
                start_time = TimeStamps[i]

            if is_there == True:
                end_time = TimeStamps[i]
            
        elif address not in Mac_Add[i] and start_time == "0":
            is_there = False 
            start_time = "0"

        else: 
            Start_Times.append(start_time)
            End_Times.append(end_time)
            is_there = False
            start_time = "0"

 
for object in aMac_Add:
    address = object
    Add_times(address)
    print(address)

    for i in range(1, len(Start_Times)):
        print(Start_Times[i], End_Times[i])   

    print("")









            