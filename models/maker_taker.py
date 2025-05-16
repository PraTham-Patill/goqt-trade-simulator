#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Maker-Taker Model Module

This module implements the MakerTakerModel class, which simulates and analyzes
the cost implications of maker-taker fee structures in trading venues.
"""

import numpy as np
import pandas as pd


class MakerTakerModel:
    """Simulates and analyzes maker-taker fee structures in trading venues."""
    
    def __init__(self, maker_rebate, taker_fee, spread, fill_probability):
        """Initialize the Maker-Taker model with market parameters.
        
        Args:
            maker_rebate (float): Rebate received for providing liquidity (bps)
            taker_fee (float): Fee paid for taking liquidity (bps)
            spread (float): Average bid-ask spread (bps)
            fill_probability (float): Probability of limit order fill (0-1)
        """
        # Convert basis points to decimal
        self.maker_rebate = maker_rebate / 10000
        self.taker_fee = taker_fee / 10000
        self.spread = spread / 10000
        self.fill_probability = fill_probability
    
    def calculate_expected_cost(self, order_size, price, is_buy, strategy='taker'):
        """Calculate the expected cost of executing an order.
        
        Args:
            order_size (float): Size of the order
            price (float): Current mid-price
            is_buy (bool): True for buy orders, False for sell orders
            strategy (str): 'taker', 'maker', or 'mixed'
        
        Returns:
            float: Expected execution cost
        """
        if strategy not in ['taker', 'maker', 'mixed']:
            raise ValueError("Strategy must be 'taker', 'maker', or 'mixed'")
        
        # Calculate half spread
        half_spread = self.spread / 2
        
        # Calculate base cost (without fees)
        base_cost = order_size * price
        
        if strategy == 'taker':
            # Taker strategy: cross the spread and pay taker fee
            spread_cost = base_cost * half_spread if is_buy else -base_cost * half_spread
            fee_cost = base_cost * self.taker_fee
            expected_cost = base_cost + spread_cost + fee_cost
        
        elif strategy == 'maker':
            # Maker strategy: post limit order, receive rebate if filled
            spread_cost = -base_cost * half_spread if is_buy else base_cost * half_spread
            rebate = -base_cost * self.maker_rebate
            
            # Expected cost considering fill probability
            filled_cost = base_cost + spread_cost + rebate
            unfilled_cost = base_cost  # Assume market order at mid-price if unfilled
            expected_cost = self.fill_probability * filled_cost + (1 - self.fill_probability) * unfilled_cost
        
        else:  # mixed strategy
            # Allocate order between maker and taker based on optimal ratio
            optimal_ratio = self.calculate_optimal_maker_ratio(is_buy)
            
            # Calculate costs for each portion
            maker_size = order_size * optimal_ratio
            taker_size = order_size * (1 - optimal_ratio)
            
            maker_cost = self.calculate_expected_cost(maker_size, price, is_buy, 'maker')
            taker_cost = self.calculate_expected_cost(taker_size, price, is_buy, 'taker')
            
            expected_cost = maker_cost + taker_cost
        
        return expected_cost
    
    def calculate_optimal_maker_ratio(self, is_buy):
        """Calculate the optimal ratio of order to place as maker vs taker.
        
        Args:
            is_buy (bool): True for buy orders, False for sell orders
        
        Returns:
            float: Optimal maker ratio (0-1)
        """
        # Calculate expected cost differential between maker and taker per unit
        half_spread = self.spread / 2
        
        # For buy orders
        if is_buy:
            taker_cost = half_spread + self.taker_fee
            maker_cost = -half_spread - self.maker_rebate
        # For sell orders
        else:
            taker_cost = -half_spread + self.taker_fee
            maker_cost = half_spread - self.maker_rebate
        
        # Adjust maker cost for fill probability
        expected_maker_cost = self.fill_probability * maker_cost
        
        # Calculate cost differential
        cost_diff = taker_cost - expected_maker_cost
        
        # If maker is cheaper, use more maker orders
        if cost_diff > 0:
            # Simple linear model: more cost difference = more maker orders
            # Normalize to ensure ratio is between 0 and 1
            optimal_ratio = min(max(cost_diff / (self.spread + self.taker_fee + self.maker_rebate), 0), 1)
        else:
            # If taker is cheaper, use all taker orders
            optimal_ratio = 0
        
        return optimal_ratio
    
    def simulate_execution(self, order_size, price, is_buy, num_simulations=1000):
        """Simulate execution outcomes for different strategies.
        
        Args:
            order_size (float): Size of the order
            price (float): Current mid-price
            is_buy (bool): True for buy orders, False for sell orders
            num_simulations (int): Number of simulations to run
        
        Returns:
            pandas.DataFrame: Simulation results
        """
        # Initialize results
        results = {
            'Strategy': [],
            'Execution_Cost': [],
            'Simulation': []
        }
        
        # Strategies to simulate
        strategies = ['taker', 'maker', 'mixed']
        
        # Run simulations
        for sim in range(num_simulations):
            # Randomize fill probability for this simulation
            sim_fill_prob = np.random.beta(self.fill_probability * 10, (1 - self.fill_probability) * 10)
            temp_model = MakerTakerModel(self.maker_rebate * 10000, self.taker_fee * 10000, 
                                         self.spread * 10000, sim_fill_prob)
            
            for strategy in strategies:
                cost = temp_model.calculate_expected_cost(order_size, price, is_buy, strategy)
                
                results['Strategy'].append(strategy)
                results['Execution_Cost'].append(cost)
                results['Simulation'].append(sim)
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        # Calculate summary statistics
        summary = df_results.groupby('Strategy')['Execution_Cost'].agg(
            ['mean', 'std', 'min', 'max']
        ).reset_index()
        
        return df_results, summary
    
    def analyze_venue_selection(self, venues, order_size, price, is_buy):
        """Analyze and compare different trading venues.
        
        Args:
            venues (list): List of dictionaries with venue parameters
            order_size (float): Size of the order
            price (float): Current mid-price
            is_buy (bool): True for buy orders, False for sell orders
        
        Returns:
            pandas.DataFrame: Venue comparison results
        """
        # Initialize results
        results = {
            'Venue': [],
            'Strategy': [],
            'Expected_Cost': [],
            'Expected_Savings': []
        }
        
        # Strategies to analyze
        strategies = ['taker', 'maker', 'mixed']
        
        # Base cost (without fees or spread)
        base_cost = order_size * price
        
        # Analyze each venue
        for venue in venues:
            venue_name = venue['name']
            venue_model = MakerTakerModel(
                venue['maker_rebate'],
                venue['taker_fee'],
                venue['spread'],
                venue['fill_probability']
            )
            
            for strategy in strategies:
                cost = venue_model.calculate_expected_cost(order_size, price, is_buy, strategy)
                savings = base_cost - cost if is_buy else cost - base_cost
                
                results['Venue'].append(venue_name)
                results['Strategy'].append(strategy)
                results['Expected_Cost'].append(cost)
                results['Expected_Savings'].append(savings)
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        # Find best venue-strategy combination
        if is_buy:
            best_idx = df_results['Expected_Cost'].idxmin()
        else:
            best_idx = df_results['Expected_Cost'].idxmax()
        
        best_combination = df_results.loc[best_idx]
        
        return df_results, best_combination
