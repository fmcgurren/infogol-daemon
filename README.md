# infogol-daemon
infogol-daemon is a bot that pulls Expected Goals (xG) betting recommendations from the Infogol API and maps
them to Markets on the Betfair Exchange. Upon successful mapping it will automatically wager according to configured thresholds using Betfairs Exchange API.

## Expected Goals (xG)

> Expected goals (xG) quantifies the quality of any given 
> scoring opportunity, giving each chance a probability of 
> being scored. The higher the probability, the better the 
> chance. xG provides a descriptive look back at individual 
> games or over a longer period of time, helping to give an 
> insight into future performance.

Futher information on xG modelling can be found [here](https://www.infogol.net/blog/infogol-football-app/an-introduction-to-expected-goals-11112016).

## Betfair Configuration
The daemon uses Betfair non interactive (bot) login which requires a certificate. Further details are available [here](https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Non-Interactive+%28bot%29+login).

In addition to creating the necessary certificate the bot requires the following environment variables to be configured:

```
BETFAIR_LIVE_KEY
BETFAIR_USERNAME
BETFAIR_PASSWORD
```

## Bot Configuration
Under 'Infogol Settings' of daemon.py configure the following as required:

```python
# Infogol Settings
minConfidence = 4 # the min confidence of tips to consider
daysAhead = 1 # how many days ahead to consider
placementThresholdHours = 4  # issue with south american matches
overroundThreshold = 103  # the spread in prices as an indicator of market liquidity
```
## Usage

```sh
$ python3 daemon.py
```

## Notes
1. betfair.py is a fork of Betfairs API-NG-sample-code [here](https://github.com/betfair/API-NG-sample-code/tree/master/python).
2. The code responsible for placing wagers has been commented out (see below), uncomment as necessary:

```python
  # only place if no orders in the Market
  if currentOrders['currentOrders'] == []:
      mapping.PrintYourself()
      # betfair.placeBet(mapping.marketId, mapping.selectionId,
      #                 stake, mapping.currentBackPrice)
  else:
      print('Bet already placed: ' + mapping.eventName + ' market: ' +
            mapping.marketName + ' verdict: ' + mapping.selectionName)
```
