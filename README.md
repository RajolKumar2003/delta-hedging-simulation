# Delta Hedging Simulation

In this project I sell a call option and check how much delta hedging reduces the risk.

## Why I made this
I am applying for options trading roles and wanted a small project on how an options desk actually manages risk. I picked delta hedging because it connects two things I studied, stochastic calculus and Black-Scholes, to a real trading problem.

## Idea
If I sell a call, I lose money when the stock goes up. To cover this I hold `delta` shares of the stock, where delta = N(d1) from Black-Scholes. I can only rebalance at fixed times, not continuously, so some risk is always left. I wanted to see how this leftover risk changes when I hedge more often.

## What I did
- Simulated the stock with Geometric Brownian Motion: `S(t+dt) = S(t) * exp((r - sigma^2/2)dt + sigma*sqrt(dt)*Z)`
- Priced the call with Black-Scholes and used its delta as the hedge ratio
- 5000 paths, S0 = K = 100, sigma = 20%, r = 5%, T = 1 year
- Rebalanced 4, 12, 52 and 252 times a year and compared with not hedging

## Results
| Case | Std of P&L | Risk reduced |
|---|---|---|
| Unhedged | 15.50 | - |
| Hedged 4 times/year | 3.16 | 79.6% |
| Hedged 12 times/year | 1.93 | 87.5% |
| Hedged 52 times/year | 0.96 | 93.8% |
| Hedged 252 times/year | 0.44 | 97.2% |

Mean P&L is close to 0 in all cases, and the leftover risk goes down roughly like 1/sqrt(n).

![results](hedging_results.png)

## How to run
```
pip install numpy scipy matplotlib
python delta_hedging.py
```

## Things I did not include
Transaction costs, changing volatility and jumps in the stock price. With these the results would be worse than shown here.
