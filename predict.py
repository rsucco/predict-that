import xml.etree.ElementTree as ET
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
    contracts = testMarket[3].copy()
    contracts = dict(sorted(contracts.items(), key=lambda x: x[1]))
    newMarket = testMarket.copy()
    newMarket[3] = contracts.copy()
    
    highestReturn = 0
    highestReturnNumBets = 0
    highestReturnPayout = 0
    highestReturnProfit = 0
    highestReturnNumShares = 0
    highestContracts = []
    
    # For N bets where Price < $1, Payout is (N - 1) * $1. Initial investment is sum(Prices)
    # Profit is Payout minus Initial Investment. Return rate (in percentage) is Profit / Initial investment * 100
    # Total amount of shares we can buy is equal to 850 / min(Prices)
    numBets = 1
    totalInvestment = 0.0
    for contract in contracts:
        contractPrice = contracts[contract]
        totalInvestment += contractPrice
        payout = numBets - 1
        profit = payout - totalInvestment
        if (totalInvestment != 0):
            returnPercentage = profit / totalInvestment * 100
        else:
            returnPercentage = 0

        if (returnPercentage > highestReturn):
            highestReturn = returnPercentage
            highestReturnNumBets = numBets
            highestReturnNumShares = round(850 / contractPrice)
            highestReturnPayout = payout
            highestReturnProfit = profit
            
        numBets += 1

    # We're profitable!
    if (highestReturn > 1):
        contracts = list(sorted(contracts.items(), key=lambda x: x[1]))
        
        for bet in range(highestReturnNumBets):
            highestContracts.append(contracts[bet])
            
        highestContracts = [list(contract) for contract in highestContracts]
        newMarket[3] = highestContracts.copy()
        newMarket.append(highestReturn)
        newMarket.append(highestReturnNumBets)
        newMarket.append(highestReturnNumShares)
        newMarket.append(highestReturnPayout)
        newMarket.append(highestReturnProfit)
        return newMarket
    else:
        return None

def printMarkets(markets, numMarkets = 0):
    # If the user passed either no input or too many markets, print all the markets. Otherwise, print what they asked for
    if numMarkets == '':
        numMarkets = 0
    else:
        numMarkets = int(numMarkets)
    if (numMarkets <= 0 or numMarkets > len(markets)):
        numMarkets = len(markets)
        
    # There's almost certainly a more effecient and pythonic way to represent the data for the market, but I didn't expect  
    # so much to be relevant when I started so it's all basically just one big list. Here's what the indices correspond to:
    # [0]: MarketID
    # [1]: ShortName
    # [2]: TimeStamp
    # [3]: Contracts
    # [4]: EndDate
    # [5]: Guaranteed Return Rate
    # [6]: Number of bets
    # [7]: Number of shares per bet
    # [8]: Total payout
    # [9]: Total profit
        
    clear()
    timestamp = markets[0][2][0].text
    print("Data as of " + str(timestamp))
    print("")
    print("--------------")
    print("")
    for i in range(numMarkets):
        market = markets[i]
        marketID = market[0][0].text
        marketName = market[1][0].text
        contracts = market[3]
        endDate = market[4].text
        guaranteedReturnRate = "{:.2f}".format(market[5])
        numBets = market[6]
        sharesPerBet = market[7]
        totalPayout = "{:.2f}".format(market[8] * sharesPerBet)
        totalInvestment = "{:.2f}".format(sum(x[1] for x in contracts) * sharesPerBet)
        totalProfit = "{:.2f}".format(market[9] * sharesPerBet)
        print("Market ID: " + marketID)
        print(marketName)
        if (endDate != "NA" and endDate != "N/A"):
            print("")
            print("End Date: " + endDate)  
        print("")
        print("An initial investment of $" + totalInvestment + " will pay out at least $" + totalPayout + ", for a guaranteed profit of $" + totalProfit + ".")
        print("Guaranteed return rate: " + guaranteedReturnRate + "%")
        print("")
        print(str(numBets) + " bets: ")
       
        for contract in contracts:
            contractName = "{:<25}".format(contract[0])
            investment = "{:.2f}".format(contract[1] * sharesPerBet)
            sharePrice = "{:.2f}".format(contract[1])
            print(contractName + str(sharesPerBet) + " shares at $" + sharePrice + " per share (Total invested in this contract: $" + str(investment) + ")")
        print("")
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
            # We queried too many times in a row. Back off a bit
            time.sleep(45)
            getMarkets(mode, numMarkets)
            break
            

        # Create the list of profitable markets
        profitableMarkets = []
        for market in root.Markets[0].MarketData:
            # Initialize the list for this market
            thisMarket = []

            # Add each contract to the market so we can check its total profitability
            contracts = {}
            endDate = market.Contracts[0].MarketContract[0].DateEnd[0]     
            for contract in market.Contracts[0].MarketContract:
                # If this fails, that means that no shares of 'no' are trading
                try:
                    contractName = contract.Name[0].text
                    #contractNames.append(contractName)
                    contractPrice = float(contract.BestBuyNoCost[0].text)
                    #contractPrices.append(contractPrice)
                    contracts[contractName] = contractPrice
                except AttributeError:
                    pass
                
            # Create the foundation of the market structure before checking its profitability
            thisMarket.append(market.ID)
            thisMarket.append(market.ShortName)
            thisMarket.append(market.TimeStamp)
            thisMarket.append(contracts)
            thisMarket.append(endDate)

            # Check the profitability of the market. If it's profitable, add it to the list of profitable markets.
            isProfitable = getProfitability(thisMarket)
            if (isProfitable is not None and len(isProfitable) >= 10):
                profitableMarkets.append(isProfitable)
                
        # Sort the list of markets by guaranteed return rate.
        # TODO: Add ability to also sort by end date and total profit
        profitableMarkets = sorted(profitableMarkets, key=lambda x: x[5], reverse=True)

                
        # Print out the data on the markets
        printMarkets(profitableMarkets, numMarkets)
        
        # If this is a one-time run, get out of the loop. Otherwise, wait 20 seconds, then go again. Data is updated every minute, 
        # and querying it too regularly results in HTTP 429 errors. 20 seconds seems to be a good compromise.
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