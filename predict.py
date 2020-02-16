import xml.etree.ElementTree as ET

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
    bets = sorted(market[3].copy(), key=float)
    
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


# Parse the data file and get the ElementTree root
tree = ET.parse("./sampleallmarkets.xml").getroot()
root = parseNodes(tree)

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
            buyText = "{:.2f}".format(bestBuy)
        except AttributeError:
            pass
        
    thisMarket.append(market.ID)
    thisMarket.append(market.ShortName)
    thisMarket.append(contractNames)
    thisMarket.append(contractPrices)
    isProfitable = getProfitability(thisMarket)
    if (isProfitable is not None):
        profitableMarkets.append(isProfitable)

profitableMarkets = sorted(profitableMarkets,key=lambda l:l[4], reverse=True)

for market in profitableMarkets:
    guaranteedReturn = round((market[4] - 1) * 100, 3)
    maxBet = market[5] * 850.0
    guaranteedProfit = maxBet * guaranteedReturn / 100
    print("Market ID: " + market[0][0].text)
    print(market[1][0].text)
    print("Guaranteed return rate: " + str(guaranteedReturn) + "%")
    print("Maximum bet: $" + str(maxBet) + " for a guaranteed profit of $" + str(guaranteedProfit))
    print(str(market[5]) + " bets: "),
    for i in range(market[5]):
        print(market[2][i] + "  (" + str(market[3][i]) + "%)")
    print("--------------")
    print("")