import csv
import QSTK.qstkutil.qsdateutil as dateUtil
import QSTK.qstkutil.DataAccess as dataAccess
import datetime
import pandas
import sys
from decimal import Decimal
def marketSimulator():
    # command line input
    startingCash = sys.argv[1]
    orders = sys.argv[2]
    values = sys.argv[3]
    # to implement read/write functionality
    csvReader = csv.reader(open(orders, 'r'))
    csvWriter = csv.writer(open(values, 'wb'))
    inputData = []
    symbols = []
    dates = []
    for each in csvReader:
        inputData.append(each)
        dates.append(datetime.datetime(int(each[0]), int(each[1]), int(each[2])))
        symbols.append(each[3])
    # to remove duplicates
    symbols = list(set(symbols))
    dates = list(set(dates))
    dates.sort()
    # from pdf
    endDate = dates[-1] + datetime.timedelta(days = 1)
    timeStamps = dateUtil.getNYSEdays(dates[0], endDate, datetime.timedelta(hours = 16))
    dataObj = dataAccess.DataAccess('Yahoo')
    keys = ['close']
    data = dataObj.get_data(timeStamps, symbols, keys)
    data_d = dict(zip(keys, data))
    prices = data_d['close']
    shares = pandas.DataFrame(0, index = timeStamps, columns = symbols)

    for each in inputData:
        symbol = each[3]
        date = datetime.datetime(int(each[0]), int(each[1]), int(each[2]), 16)
        if each[4].lower() == "buy":
            shares[symbol][date] += int(each[5])
        else:
            shares[symbol][date] -= int(each[5])
    cash = pandas.TimeSeries(0, timeStamps)
    cash[timeStamps[0]] = startingCash
    for i in range(len(timeStamps)):
        total = 0
        for s in symbols:
            total = total - shares[s][timeStamps[i]]*prices[s][timeStamps[i]]
        if i == 0:
            cash[timeStamps[i]] = cash[timeStamps[i]] + total
        else:
            cash[timeStamps[i]] = cash[timeStamps[i-1]] + total
    shares = shares.cumsum(axis = 0)
    shares["_CASH"] = cash
    prices["_CASH"] = 1.0
    total = shares*prices
    total = total.sum(axis = 1)
    for value in total.keys():
        csvWriter.writerow([value.year, value.month, value.day, total[value]])
marketSimulator()