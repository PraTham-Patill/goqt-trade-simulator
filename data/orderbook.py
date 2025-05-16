#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Orderbook Module

This module implements the Orderbook class, which maintains the current state
of the market orderbook and provides methods for analysis.
"""

import time
import json
import numpy as np
from collections import defaultdict


class Orderbook:
    """Maintains the current state of the market orderbook and provides methods for analysis."""
    
    def __init__(self, symbol):
        """Initialize the orderbook for a specific symbol.
        
        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC-USDT')
        """
        self.symbol = symbol
        self.bids = {}  # Price -> Volume mapping
        self.asks = {}  # Price -> Volume mapping
        self.last_update_time = None
        self.last_update_id = None
        self.observers = []
    
    def register_observer(self, observer):
        """Register an observer to be notified of orderbook updates.
        
        Args:
            observer: An object with an on_orderbook_update method
        """
        if observer not in self.observers:
            self.observers.append(observer)
    
    def unregister_observer(self, observer):
        """Unregister an observer.
        
        Args:
            observer: A previously registered observer
        """
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self):
        """Notify all registered observers of an orderbook update."""
        for observer in self.observers:
            observer.on_orderbook_update(self)
    
    def update(self, data):
        """Process an orderbook update from the WebSocket feed.
        
        Args:
            data (dict): The orderbook update data from the WebSocket feed
        
        Returns:
            bool: True if the orderbook was updated, False otherwise
        """
        try:
            # Process update based on exchange format
            # This example assumes OKX format
            if 'data' not in data:
                return False
            
            orderbook_data = data['data'][0]
            
            # Check if this is a newer update than what we have
            update_id = int(orderbook_data.get('seqId', 0))
            if self.last_update_id is not None and update_id <= self.last_update_id:
                return False
            
            # Update bids
            if 'bids' in orderbook_data:
                for bid in orderbook_data['bids']:
                    price = float(bid[0])
                    volume = float(bid[1])
                    
                    if volume > 0:
                        self.bids[price] = volume
                    else:
                        if price in self.bids:
                            del self.bids[price]
            
            # Update asks
            if 'asks' in orderbook_data:
                for ask in orderbook_data['asks']:
                    price = float(ask[0])
                    volume = float(ask[1])
                    
                    if volume > 0:
                        self.asks[price] = volume
                    else:
                        if price in self.asks:
                            del self.asks[price]
            
            # Update metadata
            self.last_update_time = time.time()
            self.last_update_id = update_id
            
            # Notify observers
            self.notify_observers()
            
            return True
        
        except Exception as e:
            print(f"Error updating orderbook: {e}")
            return False
    
    def get_best_bid(self):
        """Get the best (highest) bid price and volume.
        
        Returns:
            tuple: (price, volume) or (None, None) if no bids
        """
        if not self.bids:
            return None, None
        
        best_price = max(self.bids.keys())
        return best_price, self.bids[best_price]
    
    def get_best_ask(self):
        """Get the best (lowest) ask price and volume.
        
        Returns:
            tuple: (price, volume) or (None, None) if no asks
        """
        if not self.asks:
            return None, None
        
        best_price = min(self.asks.keys())
        return best_price, self.asks[best_price]
    
    def get_mid_price(self):
        """Calculate the mid price between best bid and best ask.
        
        Returns:
            float: The mid price or None if orderbook is empty
        """
        best_bid, _ = self.get_best_bid()
        best_ask, _ = self.get_best_ask()
        
        if best_bid is None or best_ask is None:
            return None
        
        return (best_bid + best_ask) / 2
    
    def get_spread(self):
        """Calculate the bid-ask spread.
        
        Returns:
            float: The spread or None if orderbook is empty
        """
        best_bid, _ = self.get_best_bid()
        best_ask, _ = self.get_best_ask()
        
        if best_bid is None or best_ask is None:
            return None
        
        return best_ask - best_bid
    
    def get_spread_percentage(self):
        """Calculate the bid-ask spread as a percentage of the mid price.
        
        Returns:
            float: The spread percentage or None if orderbook is empty
        """
        spread = self.get_spread()
        mid_price = self.get_mid_price()
        
        if spread is None or mid_price is None or mid_price == 0:
            return None
        
        return (spread / mid_price) * 100
    
    def get_depth(self, side, price_levels=10):
        """Get the orderbook depth for a specific side.
        
        Args:
            side (str): 'bids' or 'asks'
            price_levels (int): Number of price levels to include
        
        Returns:
            list: List of (price, volume) tuples
        """
        if side not in ['bids', 'asks']:
            raise ValueError("Side must be 'bids' or 'asks'")
        
        book_side = self.bids if side == 'bids' else self.asks
        
        # Sort price levels
        sorted_levels = sorted(
            book_side.items(),
            key=lambda x: x[0],
            reverse=(side == 'bids')
        )
        
        return sorted_levels[:price_levels]
    
    def calculate_slippage(self, size, side):
        """Estimate slippage for a given trade size and side.
        
        Args:
            size (float): The trade size
            side (str): 'buy' or 'sell'
        
        Returns:
            float: The estimated slippage as a percentage
        """
        if side not in ['buy', 'sell']:
            raise ValueError("Side must be 'buy' or 'sell'")
        
        book_side = self.asks if side == 'buy' else self.bids
        
        # Sort price levels
        sorted_levels = sorted(
            book_side.items(),
            key=lambda x: x[0],
            reverse=(side == 'sell')
        )
        
        if not sorted_levels:
            return None
        
        # Calculate weighted average price
        remaining_size = size
        total_cost = 0
        
        for price, volume in sorted_levels:
            if remaining_size <= 0:
                break
            
            executed_volume = min(volume, remaining_size)
            total_cost += executed_volume * price
            remaining_size -= executed_volume
        
        # If we couldn't fill the entire order
        if remaining_size > 0:
            # Use the last price for the remaining size
            total_cost += remaining_size * sorted_levels[-1][0]
        
        # Calculate slippage
        best_price = sorted_levels[0][0]
        expected_cost = size * best_price
        
        if expected_cost == 0:
            return None
        
        slippage = (total_cost - expected_cost) / expected_cost
        
        # For sell orders, slippage is negative when price decreases
        if side == 'sell':
            slippage = -slippage
        
        return slippage
    
    def get_liquidity_distribution(self, side, price_range_pct=0.01, bins=10):
        """Get the distribution of liquidity within a price range.
        
        Args:
            side (str): 'bids' or 'asks'
            price_range_pct (float): Price range as percentage of mid price
            bins (int): Number of bins for the distribution
        
        Returns:
            tuple: (bin_edges, volumes) or (None, None) if orderbook is empty
        """
        if side not in ['bids', 'asks']:
            raise ValueError("Side must be 'bids' or 'asks'")
        
        mid_price = self.get_mid_price()
        if mid_price is None:
            return None, None
        
        book_side = self.bids if side == 'bids' else self.asks
        
        # Calculate price range
        price_range = mid_price * price_range_pct
        
        if side == 'bids':
            min_price = mid_price - price_range
            max_price = mid_price
        else:  # asks
            min_price = mid_price
            max_price = mid_price + price_range
        
        # Create bins
        bin_edges = np.linspace(min_price, max_price, bins + 1)
        volumes = np.zeros(bins)
        
        # Distribute volumes into bins
        for price, volume in book_side.items():
            if min_price <= price <= max_price:
                bin_index = int((price - min_price) / (max_price - min_price) * bins)
                if bin_index == bins:  # Handle edge case
                    bin_index = bins - 1
                volumes[bin_index] += volume
        
        return bin_edges, volumes
    
    def to_dict(self):
        """Convert the orderbook to a dictionary representation.
        
        Returns:
            dict: The orderbook as a dictionary
        """
        return {
            'symbol': self.symbol,
            'bids': dict(self.get_depth('bids', price_levels=10)),
            'asks': dict(self.get_depth('asks', price_levels=10)),
            'last_update_time': self.last_update_time,
            'last_update_id': self.last_update_id,
            'mid_price': self.get_mid_price(),
            'spread': self.get_spread(),
            'spread_percentage': self.get_spread_percentage()
        }
    
    def __str__(self):
        """String representation of the orderbook.
        
        Returns:
            str: The orderbook as a string
        """
        return json.dumps(self.to_dict(), indent=2)
