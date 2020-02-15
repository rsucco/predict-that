numCandidates = int(input("How many candidates have >= 1% odds of winning? "))
totalCost = 0
scenarios = []
for i in range(1, numCandidates + 1):
     noOdds = input("Enter the cost in cents of a no contract for candidates number " + str(i) + ": ")
     totalCost += float(noOdds) * 8.5
     guaranteedReturn = (i - 1) * 850.0
     guaranteedProfit = guaranteedReturn - totalCost
     returnPercentage = round((guaranteedReturn / totalCost), 2)
     possiblePercentage = round(((guaranteedReturn + 850.0) / totalCost), 2)
     scenarios.append("Betting the max on the top " + str(i) + "\
        candidates would have a total cost of " + str(totalCost) + \
         " and a guaranteed profit of " + str(guaranteedProfit) + " for\
        a guaranteed return percentage of " + str(returnPercentage) \
         + "% and a possible maximum return of " + str(possiblePercentage) + "%.")

for scenario in scenarios:
     print(scenario)