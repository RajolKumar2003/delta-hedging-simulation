# delta hedging simulation
# idea: I sell a call option and see how much the hedge reduces my risk
# only two things used: GBM for the stock and delta hedging

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm

# parameters
S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
N_PATHS = 5000
REBALANCES = [4, 12, 52, 252]   # how many times per year I rebalance
rng = np.random.default_rng(42)


# black scholes call price and delta
def d1(S, tau):
    return (np.log(S / K) + (r + 0.5 * sigma**2) * tau) / (sigma * np.sqrt(tau))


def bs_call(S, tau):
    D1 = d1(S, tau)
    D2 = D1 - sigma * np.sqrt(tau)
    return S * norm.cdf(D1) - K * np.exp(-r * tau) * norm.cdf(D2)


def bs_delta(S, tau):
    return norm.cdf(d1(S, tau))


def simulate_paths(n_steps):
    # GBM: S(t+dt) = S(t) * exp((r - sigma^2/2)dt + sigma*sqrt(dt)*Z)
    # used r as drift (risk neutral), hedged pnl doesnt depend on drift much
    dt = T / n_steps
    Z = rng.standard_normal((N_PATHS, n_steps))
    log_ret = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    S = S0 * np.exp(np.cumsum(log_ret, axis=1))
    return np.hstack([np.full((N_PATHS, 1), S0), S])


def unhedged_pnl(S):
    # sell the call, keep the premium, pay the payoff at the end
    premium = bs_call(S0, T)
    payoff = np.maximum(S[:, -1] - K, 0.0)
    return premium * np.exp(r * T) - payoff


def hedged_pnl(S):
    # sell the call, buy delta shares, then rebalance every step
    n_steps = S.shape[1] - 1
    dt = T / n_steps
    premium = bs_call(S0, T)

    delta = bs_delta(S[:, 0], T)
    cash = premium - delta * S[:, 0]   # premium used to buy the shares

    for i in range(1, n_steps):
        tau = T - i * dt
        cash *= np.exp(r * dt)                 # interest on cash
        new_delta = bs_delta(S[:, i], tau)
        cash -= (new_delta - delta) * S[:, i]  # buy/sell the difference in shares
        delta = new_delta

    cash *= np.exp(r * dt)                     # last period interest
    payoff = np.maximum(S[:, -1] - K, 0.0)
    return cash + delta * S[:, -1] - payoff    # sell shares, pay the option holder


if __name__ == "__main__":
    print(f"Option price (Black-Scholes): {bs_call(S0, T):.4f}")

    # unhedged case (daily steps just to get final prices)
    S_base = simulate_paths(252)
    pnl_un = unhedged_pnl(S_base)
    sd_un = pnl_un.std()
    print(f"\nUnhedged      : mean P&L = {pnl_un.mean():7.3f}, std = {sd_un:7.3f}")

    # hedged case for each rebalancing frequency
    results = {}
    for n in REBALANCES:
        S = simulate_paths(n)
        pnl = hedged_pnl(S)
        results[n] = pnl
        red = 100 * (1 - pnl.std() / sd_un)
        print(f"Hedged ({n:3d}x) : mean P&L = {pnl.mean():7.3f}, std = {pnl.std():7.3f}"
              f"   (risk reduced {red:5.1f}%)")

    # plots
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))

    ax[0].hist(pnl_un, bins=80, alpha=0.6, label="Unhedged")
    ax[0].hist(results[252], bins=80, alpha=0.7, label="Delta hedged (daily)")
    ax[0].set_title("P&L of a short call")
    ax[0].set_xlabel("Final P&L")
    ax[0].set_ylabel("Number of paths")
    ax[0].legend()

    stds = [results[n].std() for n in REBALANCES]
    ax[1].loglog(REBALANCES, stds, "o-", label="Simulated std of P&L")
    ref = stds[0] * np.sqrt(REBALANCES[0] / np.array(REBALANCES))
    ax[1].loglog(REBALANCES, ref, "--", label="1/sqrt(n) line")
    ax[1].set_title("Risk left vs how often I hedge")
    ax[1].set_xlabel("Rebalances per year")
    ax[1].set_ylabel("Std of P&L")
    ax[1].legend()

    plt.tight_layout()
    plt.savefig("hedging_results.png", dpi=150)
    print("\nSaved hedging_results.png")
