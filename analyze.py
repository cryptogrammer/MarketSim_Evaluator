import csv
import QSTK.qstkutil.qsdateutil as dateUtil
import QSTK.qstkutil.DataAccess as dataAccess
import datetime
import pandas
import matplotlib.pyplot as plt
import numpy
import sys

def analyze():
    values = sys.argv[1]
    benchmark = sys.argv[2]
    csvReader = csv.reader(open(values, 'r'))
    valuesPortfolio = []
    dates = []
    val = []
    for v in csvReader:
        valuesPortfolio.append(v)
    for each in valuesPortfolio:
        dates.append(datetime.datetime(int(each[0]), int(each[1]), int(each[2])))
        val.append(float(each[3]))
    df_portfolio = pandas.DataFrame(val, index = dates, columns = ["Portfolio"])
    startDate = dates[0]
    endDate = dates[-1] + datetime.timedelta(days = 1) 
    timeStamps = dateUtil.getNYSEdays(startDate, endDate, datetime.timedelta(hours = 16))
    data_d = dataAccess.DataAccess('Yahoo')
    keys = ['close']
    data = data_d.get_data(timeStamps, [benchmark], keys)
    dataDict = dict(zip(keys, data))
    prices = dataDict['close']
    scale_factor = round(float(df_portfolio['Portfolio'][0])/float(prices[benchmark][0]), 5)
    df_portfolio[benchmark] = prices[benchmark].values*scale_factor
    raw = df_portfolio.values
    returns = [[0, 0]]
    for i in range(1, len(raw)):
        returns.append([raw[i][0]/raw[i-1][0] - 1,
                          raw[i][1]/raw[i-1][1] - 1])
    mReturns = numpy.mean(returns, axis = 0)
    stDev = numpy.std(returns, axis = 0)
    totalReturns = (raw / raw[0, :])[-1]
    sharpe = mReturns / stDev * 252**0.5

    print "\nFinal value: " + ",".join(valuesPortfolio[-1])
    print "Details of the performance of the portfolio:"
    print "Date Range: " + str(datetime.datetime(startDate.year, startDate.month, startDate.day, 16)) + \
          " to " + str(datetime.datetime(endDate.year, endDate.month, endDate.day, 16) - 
            datetime.timedelta(days = 1))
    print "Sharpe Ratio: " + str(sharpe[0])
    print "Sharpe Ratio of " + benchmark + ": " + str(sharpe[1])
    print "Total Return: " + str(totalReturns[0])
    print "Total Return of " + benchmark + ": " + str(totalReturns[1])
    print "Standard Deviation: " + str(stDev[0])
    print "Standard Deviation of " + benchmark + ": " + str(stDev[1])
    print "Average Daily Return: " + str(mReturns[0])
    print "Average Daily Return of " + benchmark + ": " + str(mReturns[1])


    plt.clf()
    plt.figure(figsize = (15,12))
    plt.plot(timeStamps, df_portfolio)
    plt.title("Portfolio vs Benchmark")
    plt.legend(["Portfolio", benchmark])
    plt.xlabel("Date")
    plt.ylabel("Prices")
    plt.savefig("orders2.pdf", format="pdf")

analyze()