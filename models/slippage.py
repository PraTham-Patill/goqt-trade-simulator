#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Slippage Model Module

This module implements the SlippageModel class, which estimates price slippage
based on order size, market depth, and volatility.
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


class SlippageModel:
    """Estimates price slippage based on order size, market depth, and volatility."""
    
    def __init__(self, market_impact_factor=0.1, volatility=0.0, depth_factor=1.0):
        """Initialize the Slippage model with market parameters.
        
        Args:
            market_impact_factor (float): Factor for market impact (0-1)
            volatility (float): Asset price volatility (annualized)
            depth_factor (float): Factor for market depth adjustment
        """
        self.market_impact_factor = market_impact_factor
        self.volatility = volatility
        self.depth_factor = depth_factor
        self.fitted_params = None
    
    def square_root_model(self, order_size, price, daily_volume):
        """Calculate slippage using the square root model.
        
        Args:
            order_size (float): Size of the order
            price (float): Current asset price
            daily_volume (float): Average daily trading volume
        
        Returns:
            float: Estimated slippage in price units
        """
        # Calculate order size as percentage of daily volume
        size_ratio = order_size / daily_volume
        
        # Calculate slippage using square root formula
        slippage_bps = self.market_impact_factor * np.sqrt(size_ratio) * 10000
        
        # Convert to price units
        slippage = (slippage_bps / 10000) * price
        
        return slippage
    
    def linear_model(self, order_size, price, daily_volume):
        """Calculate slippage using a linear model.
        
        Args:
            order_size (float): Size of the order
            price (float): Current asset price
            daily_volume (float): Average daily trading volume
        
        Returns:
            float: Estimated slippage in price units
        """
        # Calculate order size as percentage of daily volume
        size_ratio = order_size / daily_volume
        
        # Calculate slippage using linear formula
        slippage_bps = self.market_impact_factor * size_ratio * 10000
        
        # Convert to price units
        slippage = (slippage_bps / 10000) * price
        
        return slippage
    
    def power_law_model(self, order_size, price, daily_volume, exponent=0.6):
        """Calculate slippage using a power law model.
        
        Args:
            order_size (float): Size of the order
            price (float): Current asset price
            daily_volume (float): Average daily trading volume
            exponent (float): Power law exponent
        
        Returns:
            float: Estimated slippage in price units
        """
        # Calculate order size as percentage of daily volume
        size_ratio = order_size / daily_volume
        
        # Calculate slippage using power law formula
        slippage_bps = self.market_impact_factor * (size_ratio ** exponent) * 10000
        
        # Convert to price units
        slippage = (slippage_bps / 10000) * price
        
        return slippage
    
    def calculate_slippage(self, order_size, price, daily_volume, model='square_root'):
        """Calculate slippage using the specified model.
        
        Args:
            order_size (float): Size of the order
            price (float): Current asset price
            daily_volume (float): Average daily trading volume
            model (str): Model to use ('square_root', 'linear', 'power_law', or 'fitted')
        
        Returns:
            float: Estimated slippage in price units
        """
        if model == 'square_root':
            return self.square_root_model(order_size, price, daily_volume)
        elif model == 'linear':
            return self.linear_model(order_size, price, daily_volume)
        elif model == 'power_law':
            return self.power_law_model(order_size, price, daily_volume)
        elif model == 'fitted' and self.fitted_params is not None:
            # Use fitted model parameters
            a, b = self.fitted_params
            size_ratio = order_size / daily_volume
            slippage_bps = a * (size_ratio ** b) * 10000
            return (slippage_bps / 10000) * price
        else:
            raise ValueError("Invalid model or fitted model not available")
    
    def fit_model(self, historical_data):
        """Fit the slippage model to historical data.
        
        Args:
            historical_data (pandas.DataFrame): DataFrame with columns:
                - order_size: Size of executed orders
                - price: Price at time of order
                - daily_volume: Daily trading volume
                - slippage: Observed slippage
        
        Returns:
            tuple: (a, b) parameters of the fitted power law model
        """
        # Define power law function for fitting
        def power_law(x, a, b):
            return a * (x ** b)
        
        # Calculate size ratio
        historical_data['size_ratio'] = historical_data['order_size'] / historical_data['daily_volume']
        
        # Calculate slippage in basis points
        historical_data['slippage_bps'] = (historical_data['slippage'] / historical_data['price']) * 10000
        
        # Fit power law model
        popt, _ = curve_fit(
            power_law, 
            historical_data['size_ratio'].values, 
            historical_data['slippage_bps'].values,
            bounds=([0, 0], [1, 2])  # Constrain parameters to reasonable ranges
        )
        
        # Store fitted parameters
        self.fitted_params = popt
        
        return popt
    
    def adjust_for_volatility(self, base_slippage, time_horizon_hours=1):
        """Adjust slippage estimate based on volatility.
        
        Args:
            base_slippage (float): Base slippage estimate
            time_horizon_hours (float): Time horizon for execution in hours
        
        Returns:
            float: Volatility-adjusted slippage
        """
        # Convert annualized volatility to the time horizon
        vol_factor = self.volatility * np.sqrt(time_horizon_hours / (252 * 6.5))
        
        # Add volatility component to slippage
        adjusted_slippage = base_slippage * (1 + vol_factor)
        
        return adjusted_slippage
    
    def adjust_for_market_depth(self, base_slippage, depth_ratio):
        """Adjust slippage estimate based on market depth.
        
        Args:
            base_slippage (float): Base slippage estimate
            depth_ratio (float): Ratio of order size to available liquidity at best prices
        
        Returns:
            float: Depth-adjusted slippage
        """
        # Adjust slippage based on market depth
        depth_adjustment = 1 + (depth_ratio * self.depth_factor)
        adjusted_slippage = base_slippage * depth_adjustment
        
        return adjusted_slippage
    
    def simulate_slippage(self, order_sizes, price, daily_volume, num_simulations=100):
        """Simulate slippage for different order sizes.
        
        Args:
            order_sizes (list): List of order sizes to simulate
            price (float): Current asset price
            daily_volume (float): Average daily trading volume
            num_simulations (int): Number of simulations per order size
        
        Returns:
            pandas.DataFrame: Simulation results
        """
        # Initialize results
        results = {
            'Order_Size': [],
            'Order_Size_Pct': [],
            'Model': [],
            'Slippage': [],
            'Slippage_Bps': [],
            'Simulation': []
        }
        
        # Models to simulate
        models = ['square_root', 'linear', 'power_law']
        
        # Run simulations
        for sim in range(num_simulations):
            # Add random noise to parameters for this simulation
            sim_impact = self.market_impact_factor * np.random.uniform(0.8, 1.2)
            sim_model = SlippageModel(sim_impact, self.volatility, self.depth_factor)
            
            for size in order_sizes:
                size_pct = size / daily_volume * 100  # Convert to percentage
                
                for model in models:
                    slippage = sim_model.calculate_slippage(size, price, daily_volume, model)
                    slippage_bps = (slippage / price) * 10000
                    
                    results['Order_Size'].append(size)
                    results['Order_Size_Pct'].append(size_pct)
                    results['Model'].append(model)
                    results['Slippage'].append(slippage)
                    results['Slippage_Bps'].append(slippage_bps)
                    results['Simulation'].append(sim)
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        # Calculate summary statistics
        summary = df_results.groupby(['Order_Size', 'Order_Size_Pct', 'Model'])['Slippage_Bps'].agg(
            ['mean', 'std', 'min', 'max']
        ).reset_index()
        
        return df_results, summary
