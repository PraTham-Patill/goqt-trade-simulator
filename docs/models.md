# Trade Simulator Models

## Overview

This document describes the mathematical models used in the Trade Simulator to estimate transaction costs and market impact for cryptocurrency trading.

## Almgren-Chriss Market Impact Model

### Theory

The Almgren-Chriss model is a mathematical framework for optimal execution of portfolio transactions. It balances the market impact cost of rapid execution against the market risk cost of slow execution.

### Implementation

Our implementation of the Almgren-Chriss model uses the following parameters:

- **Temporary Impact**: The immediate price change caused by a trade
- **Permanent Impact**: The lasting price change that remains after the trade
- **Market Volatility**: The natural price fluctuation of the asset
- **Risk Aversion**: A parameter representing the trader's sensitivity to risk

### Mathematical Formulation

The market impact cost for a trade of size X is modeled as:

```
I(X) = σ * |X|^α * sign(X)
```

Where:
- σ is the impact coefficient
- α is the impact exponent (typically 0.5-0.8)
- X is the trade size

The total cost of execution is then:

```
C = Σ(I(X_i)) + λ * σ^2 * T
```

Where:
- I(X_i) is the impact cost of each trade
- λ is the risk aversion parameter
- σ^2 is the variance of the asset price
- T is the total execution time

## Slippage Estimation Model

### Theory

Slippage is the difference between the expected price of a trade and the actual executed price. It occurs due to orderbook depth and market liquidity.

### Implementation

Our slippage model analyzes the current orderbook to estimate the expected execution price for a given trade size.

### Mathematical Formulation

For a trade of size X, the expected slippage is calculated as:

```
S(X) = Σ(V_i * (P_i - P_0)) / X
```

Where:
- V_i is the volume available at price level i
- P_i is the price at level i
- P_0 is the best available price
- X is the total trade size

## Maker/Taker Proportion Model

### Theory

The maker/taker proportion estimates what percentage of an order will be executed as a maker (adding liquidity) versus a taker (removing liquidity).

### Implementation

This model analyzes historical order execution data and current market conditions to predict the maker/taker split.

### Mathematical Formulation

The maker proportion M for a trade is estimated as:

```
M = f(X, V, σ, τ)
```

Where:
- X is the trade size
- V is the current market volume
- σ is the market volatility
- τ is the order placement strategy parameter

## Fee Calculation

### Theory

Fees are calculated based on the exchange's fee structure and the maker/taker proportion of the trade.

### Implementation

The fee calculator uses the exchange's current fee schedule and applies it to the estimated maker/taker split.

### Mathematical Formulation

The total fee F for a trade is calculated as:

```
F = X * (M * f_maker + (1-M) * f_taker)
```

Where:
- X is the trade size
- M is the maker proportion
- f_maker is the maker fee rate
- f_taker is the taker fee rate

## Net Cost Calculation

### Theory

The net cost combines all components: slippage, market impact, and fees.

### Implementation

The net cost calculator aggregates the outputs from all models to provide a comprehensive cost estimate.

### Mathematical Formulation

The total cost C for a trade is calculated as:

```
C = S(X) + I(X) + F(X)
```

Where:
- S(X) is the slippage cost
- I(X) is the market impact cost
- F(X) is the fee cost

These models provide a comprehensive framework for estimating the true cost of executing trades in cryptocurrency markets.