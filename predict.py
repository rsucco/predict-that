import xml.etree.ElementTree as ET
import requests
import urllib.request
import time
from os import system, name

# Clear screen between refreshes
def clear():
    if name == 'nt': 
        _ = system('cls') 
    else: 
        _ = system('clear') 

# Convert an ElementTree into python data structures
def parseNodes(node):
    # Make the type match up with the name of the element
    name = node.tag
    pyType = type(name, (object, ), {})
    pyObj = pyType()

    # Set attributes for the object
    for attr in node.attrib.keys():
        setattr(pyObj, attr, node.get(attr))

    # If the tag has text, add it to the object
    if node.text and node.text != '' and node.text != ' ' and node.text != '\n':
        setattr(pyObj, 'text', node.text)

    # If the tag has subtags, repeat the process on them recursively
    for cn in node:
        if not hasattr(pyObj, cn.tag):
            setattr(pyObj, cn.tag, [])
        getattr(pyObj, cn.tag).append(parseNodes(cn))

    return pyObj

def getProfitability(testMarket):
    market = testMarket.copy()
    totalCost = 0.0
    bets = sorted(market[4].copy(), key=float)
    
    highestReturn = 0
    highestReturnNumBets = 0
    for i in range(len(bets)):
        totalCost += bets[i]
        guaranteedReturn = float(i)
        if (totalCost != 0):
            returnPercentage = guaranteedReturn / totalCost
        else:
            returnPercentage = 0

        if (returnPercentage > highestReturn):
            highestReturn = returnPercentage
            highestReturnNumBets = i
    highestReturnNumBets += 1
    
    if (highestReturn > 1):
        market.append(highestReturn)
        market.append(highestReturnNumBets)
        return market

def printMarkets(markets, numMarkets = 0):
    if numMarkets == '':
        numMarkets = 0
    else:
        numMarkets = int(numMarkets)
    if (numMarkets <= 0 or numMarkets > len(markets)):
        numMarkets = len(markets)
    clear()
    print("Data as of " + str(markets[0][2][0].text))
    print("")
    print("--------------")
    print("")
    for i in range(numMarkets):
        market = markets[i]
        guaranteedReturn = round((market[6] - 1) * 100, 3)
        maxBet = market[7] * 850.0
        guaranteedProfit = maxBet * guaranteedReturn / 100
        print("Market ID: " + market[0][0].text)
        print(market[1][0].text)
        if (market[5].text != "NA" and market[5].text != "N/A"):
            print("End Date: " + market[5].text)    
        print("Guaranteed return rate: " + str(guaranteedReturn) + "%")
        print("Maximum bet: $" + str(maxBet) + " for a guaranteed profit of $" + str(guaranteedProfit))
        print(str(market[7]) + " bets: "),
        for i in range(market[7]):
            print(market[3][i] + "  (" + str(market[4][i]) + "%)")
        print("--------------")
        print("")

def getMarkets(mode = 1, numMarkets = 0):
    while True:
        # Get the data from PredictIt's API
        url = "https://www.predictit.org/api/marketdata/all/"
        request = urllib.request.Request(url)
        request.add_header("Accept", "application/xml")

        try:
            # Parse the data file and get the ElementTree root
            tree = ET.fromstring(urllib.request.urlopen(request).read())
            root = parseNodes(tree)
        except urllib.error.HTTPError:
            getMarkets(mode, numMarkets)
            break
            

        # Create the list of profitable markets
        profitableMarkets = []
        for market in root.Markets[0].MarketData:
            # Initialize the list for this market
            thisMarket = []

            # Add each contract to the market so we can check its total profitability
            contractNames = []
            contractPrices = []     
            for contract in market.Contracts[0].MarketContract:
                # If this fails, that means that no shares of 'no' are trading
                try:
                    contractName = contract.Name[0].text
                    contractNames.append(contractName)
                    bestBuy = float(contract.BestBuyNoCost[0].text)
                    contractPrices.append(bestBuy)
                except AttributeError:
                    pass
                
            thisMarket.append(market.ID)
            thisMarket.append(market.ShortName)
            thisMarket.append(market.TimeStamp)
            thisMarket.append(contractNames)
            thisMarket.append(contractPrices)
            # Get the end date either directly from the 'Contracts' element, or the 'MarketContract' element if Contract doesn't have it
            try:
                thisMarket.append(market.Contracts[0].DateEnd[0])
            except:
                thisMarket.append(market.Contracts[0].MarketContract[0].DateEnd[0])
            isProfitable = getProfitability(thisMarket)
            if (isProfitable is not None):
                profitableMarkets.append(isProfitable)

        profitableMarkets = sorted(profitableMarkets,key=lambda l:l[6], reverse=True)
        printMarkets(profitableMarkets, numMarkets)
        if mode == '2':
            break
        time.sleep(20)

# Get user input for mode of operation
print("Modes of operation:")
print("1. Monitor markets")
print("2. List all profitable markets")
mode = input("Select option (default: 1) ")
numMarkets = input("Enter number of top markets to track (default: all) ")
print("--------------")
print("")
getMarkets(mode, numMarkets)