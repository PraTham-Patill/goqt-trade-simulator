#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Almgren-Chriss Model Module

This module implements the Almgren-Chriss model for optimal execution.
It provides methods to calculate optimal trading trajectories that balance
market impact and timing risk.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize


class AlmgrenChrissModel:
    """Implementation of the Almgren-Chriss model for optimal execution."""
    
    def __init__(self, initial_price, volatility, market_impact_permanent, 
                 market_impact_temporary, risk_aversion, time_horizon):
        """Initialize the Almgren-Chriss model with market parameters.
        
        Args:
            initial_price (float): Initial asset price
            volatility (float): Asset price volatility (annualized)
            market_impact_permanent (float): Permanent market impact parameter
            market_impact_temporary (float): Temporary market impact parameter
            risk_aversion (float): Risk aversion parameter
            time_horizon (float): Time horizon for execution (in days)
        """
        self.initial_price = initial_price
        self.volatility = volatility
        self.market_impact_permanent = market_impact_permanent
        self.market_impact_temporary = market_impact_temporary
        self.risk_aversion = risk_aversion
        self.time_horizon = time_horizon
    
    def calculate_optimal_trajectory(self, total_shares, num_periods):
        """Calculate the optimal trading trajectory.
        
        Args:
            total_shares (float): Total number of shares to execute
            num_periods (int): Number of trading periods
        
        Returns:
            tuple: (times, shares_remaining, execution_sizes, expected_prices)
        """
        # Convert time horizon to seconds (assuming trading day = 6.5 hours)
        T = self.time_horizon * 6.5 * 3600
        
        # Time points
        times = np.linspace(0, T, num_periods + 1)
        dt = T / num_periods
        
        # Convert volatility to per-second
        sigma = self.volatility / np.sqrt(252 * 6.5 * 3600)
        
        # Calculate optimal trading rate
        kappa = self.market_impact_permanent
        lambda_ = self.market_impact_temporary
        alpha = self.risk_aversion
        
        # Calculate tau (time scale)
        tau = np.sqrt(lambda_ / (alpha * sigma**2))
        
        # Calculate optimal trading trajectory
        shares_remaining = np.zeros(num_periods + 1)
        execution_sizes = np.zeros(num_periods)
        expected_prices = np.zeros(num_periods + 1)
        
        # Initial conditions
        shares_remaining[0] = total_shares
        expected_prices[0] = self.initial_price
        
        # Hyperbolic sine and cosine of time horizon
        sinh_kT = np.sinh(T / tau)
        cosh_kT = np.cosh(T / tau)
        
        # Calculate trading trajectory
        for i in range(num_periods):
            t = times[i]
            # Remaining time to horizon
            time_remaining = T - t
            
            # Optimal trading rate at this time
            if time_remaining > 0:
                # Calculate shares to execute in this period
                factor = np.sinh(time_remaining / tau) / sinh_kT
                target_shares = total_shares * (1 - factor)
                execution_sizes[i] = shares_remaining[i] - target_shares
                shares_remaining[i+1] = shares_remaining[i] - execution_sizes[i]
            else:
                # Execute all remaining shares at the end
                execution_sizes[i] = shares_remaining[i]
                shares_remaining[i+1] = 0
            
            # Calculate expected price after market impact
            permanent_impact = kappa * execution_sizes[:i+1].sum()
            temporary_impact = lambda_ * execution_sizes[i]
            expected_prices[i+1] = self.initial_price - permanent_impact - temporary_impact
        
        return times, shares_remaining, execution_sizes, expected_prices
    
    def calculate_implementation_shortfall(self, total_shares, execution_sizes, expected_prices):
        """Calculate the implementation shortfall.
        
        Args:
            total_shares (float): Total number of shares to execute
            execution_sizes (numpy.ndarray): Array of execution sizes
            expected_prices (numpy.ndarray): Array of expected prices
        
        Returns:
            float: Implementation shortfall
        """
        # Calculate VWAP of the execution
        vwap = np.sum(execution_sizes * expected_prices[1:]) / total_shares
        
        # Calculate implementation shortfall
        shortfall = (self.initial_price - vwap) * total_shares
        
        return shortfall
    
    def optimize_risk_aversion(self, total_shares, num_periods, min_lambda=0.1, max_lambda=10.0):
        """Find the optimal risk aversion parameter to minimize cost.
        
        Args:
            total_shares (float): Total number of shares to execute
            num_periods (int): Number of trading periods
            min_lambda (float): Minimum risk aversion to consider
            max_lambda (float): Maximum risk aversion to consider
        
        Returns:
            float: Optimal risk aversion parameter
        """
        def objective(lambda_):
            # Set risk aversion
            self.risk_aversion = lambda_[0]
            
            # Calculate trajectory
            _, _, execution_sizes, expected_prices = self.calculate_optimal_trajectory(
                total_shares, num_periods
            )
            
            # Calculate implementation shortfall
            shortfall = self.calculate_implementation_shortfall(
                total_shares, execution_sizes, expected_prices
            )
            
            return shortfall
        
        # Optimize risk aversion
        result = minimize(objective, [(min_lambda + max_lambda) / 2], 
                          bounds=[(min_lambda, max_lambda)])
        
        # Set and return the optimal risk aversion
        self.risk_aversion = result.x[0]
        return self.risk_aversion
    
    def simulate_execution(self, total_shares, num_periods, num_simulations=100):
        """Simulate execution paths with random price paths.
        
        Args:
            total_shares (float): Total number of shares to execute
            num_periods (int): Number of trading periods
            num_simulations (int): Number of price path simulations
        
        Returns:
            pandas.DataFrame: Simulation results
        """
        # Calculate optimal trajectory
        times, shares_remaining, execution_sizes, expected_prices = self.calculate_optimal_trajectory(
            total_shares, num_periods
        )
        
        # Convert time to hours for readability
        times_hours = times / 3600
        
        # Initialize results DataFrame
        results = pd.DataFrame({
            'Time': times_hours,
            'Shares_Remaining': shares_remaining,
            'Execution_Size': np.append(execution_sizes, 0),  # Add 0 for the last period
            'Expected_Price': expected_prices
        })
        
        # Convert volatility to per-period
        T = self.time_horizon * 6.5 * 3600
        dt = T / num_periods
        sigma_dt = self.volatility * np.sqrt(dt / (252 * 6.5 * 3600))
        
        # Simulate price paths
        for sim in range(num_simulations):
            # Initialize price path with initial price
            price_path = np.zeros(num_periods + 1)
            price_path[0] = self.initial_price
            
            # Generate random price increments
            for i in range(num_periods):
                # Random price change
                price_change = np.random.normal(0, sigma_dt)
                
                # Permanent impact from previous trades
                permanent_impact = self.market_impact_permanent * execution_sizes[:i].sum()
                
                # Temporary impact from current trade
                temporary_impact = self.market_impact_temporary * execution_sizes[i]
                
                # Update price
                price_path[i+1] = price_path[i] + price_change - permanent_impact - temporary_impact
            
            # Add to results
            results[f'Price_Sim_{sim+1}'] = price_path
        
        return results
