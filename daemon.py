import datetime
import requests
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from betfair import BetfairSettings
from betfair import Betfair
from infogol import Infogol
from betmapping import BetMapping

print('\n### Infogol Betting Tips Bot ###')

""" Setup """
# Infogol Settings
minConfidence = 4
daysAhead = 1
placementThresholdHours = 4  # issue with south american matches
overroundThreshold = 103  # % value


def bettingPass():
    startDate = datetime.datetime.now()
    print('Time: %s' % startDate)

    # Betfair Login
    print('\nBetfair Login...')
    appKey = os.environ.get("BETFAIR_LIVE_KEY")
    username = os.environ.get("BETFAIR_USERNAME")
    password = os.environ.get("BETFAIR_PASSWORD")
    credentials = 'username=%s&password=%s' % (username, password)

    sessionToken = None

    if sessionToken is None:
        payload = credentials
        headers = {'X-Application': 'daemon',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        # OLD https://identitysso.betfair.com/api/certlogin
        resp = requests.post('https://identitysso-cert.betfair.com/api/certlogin',
                             data=payload, cert=('client-2048.crt', 'client-2048.key'), headers=headers)

        if resp.status_code == 200:
            resp_json = resp.json()
            print(resp_json['loginStatus'])
            print(resp_json['sessionToken'])
            sessionToken = resp_json['sessionToken']
        else:
            print("Login Request failed.")
            exit()

    bettingURL = "https://api.betfair.com/exchange/betting/json-rpc/v1"
    accountsURL = "https://api.betfair.com/exchange/account/json-rpc/v1"

    # 1. Get Infogol Tips
    print('\nGetting Infogol tips...')
    infogol = Infogol()
    filteredBets = list()
    for day in range(daysAhead):
        startDate = startDate + datetime.timedelta(days=day)
        bets = infogol.callGetBestBets(startDate, minConfidence)
        for bet in bets:
            filteredBets.append(bet)

    # print(filteredBets)

    # 2. Map bets to Betfair Markets
    settings = BetfairSettings(appKey, sessionToken, bettingURL, accountsURL)

    betfair = Betfair(settings)
    accountFunds = betfair.getAccountFunds()
    print('\nBetfair Account Funds: ' + str(accountFunds) + '\n')

    availableToBetBalance = accountFunds['availableToBetBalance']

    # determine fixed stake
    stake = round(float(availableToBetBalance) * 0.04, 2)
    if stake < 2.0:
        stake = 2.0

    print('Stake: ' + str(stake))

    betMappings = list()
    for bet in filteredBets:
        betMapping = BetMapping(bet)
        betMappings.append(betMapping)
        # betMapping.PrintYourself()

    print('\nMapping bets...')
    betMappings = betfair.map(betMappings)

    print('\nPlacing bets...')
    for mapping in betMappings:
        # ignore if not mapped
        if mapping.marketId is None:
            print(mapping.eventName + ' unmapped.')
            continue

        # ignore if too far in future
        placementDateTimeThreshold = datetime.datetime.now(
        ) + datetime.timedelta(hours=placementThresholdHours)
        eventDateTime = datetime.datetime.strptime(
            mapping.eventDateTime, '%Y-%m-%dT%H:%M:%SZ')

        if eventDateTime > placementDateTimeThreshold:
            continue

        # ignore if Market is not formed
        overround = (mapping.currentLayPrice / mapping.currentBackPrice) * 100

        if(overround > overroundThreshold):
            print(mapping.eventName + ' unformed.')
            continue

        # ignore if bet already placed
        currentOrders = betfair.listCurrentOrders(mapping.marketId)

        # only place if no orders in the Market
        if currentOrders['currentOrders'] == []:
            mapping.PrintYourself()
            # betfair.placeBet(mapping.marketId, mapping.selectionId,
            #                 stake, mapping.currentBackPrice)
        else:
            print('Bet already placed: ' + mapping.eventName + ' market: ' +
                  mapping.marketName + ' verdict: ' + mapping.selectionName)

    endDate = datetime.datetime.now()
    delta = endDate - startDate
    print('\nIteration Finished. Time: %s duration: %d secs' %
          (endDate, delta.seconds))


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(bettingPass, 'interval', minutes=1)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    bettingPass()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
