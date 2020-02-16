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

# Parse the data file and get the ElementTree root
tree = ET.parse("./sampleallmarkets.xml").getroot()
root = parseNodes(tree)

# Sample to test that parsing is working properly and that we're pulling the data we need
for market in root.Markets[0].MarketData:
    for id in market.ID:
        print("Market ID: " + id.text)
    for name in market.ShortName:
        print("Name: " + name.text)
    for contract in market.Contracts[0].MarketContract:
        
        # If this fails, that means that no shares of 'no' are trading
        try:
            contractName = contract.Name[0].text
            bestBuy = float(contract.BestBuyNoCost[0].text)
            buyText = "{:.2f}".format(bestBuy)
            print("Contract name: " + contractName)
            print("Cost to buy no: $" + buyText)
        except AttributeError:
            pass
    print("----------------------------")
    print("")
    
