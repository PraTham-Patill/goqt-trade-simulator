#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WebSocket Client Module

This module implements the WebSocketClient class, which is responsible for
establishing and maintaining connections to exchange WebSocket APIs.
"""

import json
import time
import threading
import websocket
from urllib.parse import urljoin


class WebSocketClient:
    """Establishes and maintains connections to exchange WebSocket APIs."""
    
    # WebSocket endpoints for different exchanges
    ENDPOINTS = {
        'okx': 'wss://ws.okx.com:8443/ws/v5/public',
        'binance': 'wss://stream.binance.com:9443/ws',
        'coinbase': 'wss://ws-feed.pro.coinbase.com'
    }
    
    def __init__(self, exchange, symbol, callback):
        """Initialize the WebSocket client.
        
        Args:
            exchange (str): The exchange to connect to (e.g., 'okx')
            symbol (str): The trading pair symbol (e.g., 'BTC-USDT')
            callback (callable): Function to call with received data
        """
        self.exchange = exchange.lower()
        self.symbol = symbol
        self.callback = callback
        self.ws = None
        self.connected = False
        self.reconnect_delay = 1  # Initial reconnect delay in seconds
        self.max_reconnect_delay = 60  # Maximum reconnect delay in seconds
        self.thread = None
        self.should_reconnect = True
    
    def connect(self):
        """Establish WebSocket connection and start message handling thread.
        
        Returns:
            bool: True if connection was initiated, False otherwise
        """
        if self.exchange not in self.ENDPOINTS:
            print(f"Unsupported exchange: {self.exchange}")
            return False
        
        # Create WebSocket connection
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            self.ENDPOINTS[self.exchange],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Start WebSocket connection in a separate thread
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
        
        return True
    
    def on_open(self, ws):
        """Handle WebSocket connection open event.
        
        Args:
            ws: WebSocket connection object
        """
        print(f"WebSocket connection established to {self.exchange}")
        self.connected = True
        self.reconnect_delay = 1  # Reset reconnect delay
        
        # Subscribe to orderbook channel
        self.subscribe()
    
    def subscribe(self):
        """Subscribe to the orderbook channel for the specified symbol."""
        if not self.connected:
            return
        
        # Format subscription message based on exchange
        if self.exchange == 'okx':
            # Convert symbol format if needed (e.g., BTC-USDT to BTC-USDT)
            symbol = self.symbol
            
            subscription = {
                "op": "subscribe",
                "args": [{
                    "channel": "books",
                    "instId": symbol
                }]
            }
        elif self.exchange == 'binance':
            # Convert symbol format (e.g., BTC-USDT to btcusdt)
            symbol = self.symbol.lower().replace('-', '')
            
            subscription = {
                "method": "SUBSCRIBE",
                "params": [
                    f"{symbol}@depth20@100ms"
                ],
                "id": 1
            }
        elif self.exchange == 'coinbase':
            # Convert symbol format (e.g., BTC-USDT to BTC-USDT)
            symbol = self.symbol
            
            subscription = {
                "type": "subscribe",
                "product_ids": [symbol],
                "channels": ["level2"]
            }
        else:
            print(f"Subscription not implemented for exchange: {self.exchange}")
            return
        
        # Send subscription message
        self.ws.send(json.dumps(subscription))
        print(f"Subscribed to {self.symbol} orderbook on {self.exchange}")
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages.
        
        Args:
            ws: WebSocket connection object
            message (str): The received message
        """
        try:
            # Parse message
            data = json.loads(message)
            
            # Process message based on exchange format
            if self.exchange == 'okx':
                # Check if this is an orderbook update
                if 'arg' in data and data['arg'].get('channel') == 'books':
                    # Call the callback function with the data
                    self.callback(data)
            elif self.exchange == 'binance':
                # For Binance, we need to transform the data format
                if 'lastUpdateId' in data:
                    # Transform to a common format
                    transformed_data = self.transform_binance_data(data)
                    self.callback(transformed_data)
            elif self.exchange == 'coinbase':
                # For Coinbase, we need to transform the data format
                if data.get('type') == 'snapshot' or data.get('type') == 'l2update':
                    # Transform to a common format
                    transformed_data = self.transform_coinbase_data(data)
                    self.callback(transformed_data)
        
        except json.JSONDecodeError:
            print(f"Failed to parse message: {message}")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def transform_binance_data(self, data):
        """Transform Binance orderbook data to a common format.
        
        Args:
            data (dict): Binance orderbook data
        
        Returns:
            dict: Transformed data in a common format
        """
        # Extract relevant fields
        last_update_id = data.get('lastUpdateId', 0)
        bids = data.get('bids', [])
        asks = data.get('asks', [])
        
        # Transform to common format
        return {
            'data': [{
                'seqId': last_update_id,
                'bids': bids,
                'asks': asks
            }]
        }
    
    def transform_coinbase_data(self, data):
        """Transform Coinbase orderbook data to a common format.
        
        Args:
            data (dict): Coinbase orderbook data
        
        Returns:
            dict: Transformed data in a common format
        """
        # Extract relevant fields
        message_type = data.get('type')
        product_id = data.get('product_id')
        sequence = data.get('sequence', 0)
        
        if message_type == 'snapshot':
            bids = data.get('bids', [])
            asks = data.get('asks', [])
        elif message_type == 'l2update':
            # For l2update, we need to handle changes
            changes = data.get('changes', [])
            bids = [change[1:] for change in changes if change[0] == 'buy']
            asks = [change[1:] for change in changes if change[0] == 'sell']
        else:
            bids = []
            asks = []
        
        # Transform to common format
        return {
            'data': [{
                'seqId': sequence,
                'bids': bids,
                'asks': asks
            }]
        }
    
    def on_error(self, ws, error):
        """Handle WebSocket error event.
        
        Args:
            ws: WebSocket connection object
            error: The error that occurred
        """
        print(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close event.
        
        Args:
            ws: WebSocket connection object
            close_status_code: Status code for the connection close
            close_msg: Close message
        """
        self.connected = False
        print(f"WebSocket connection closed: {close_status_code} {close_msg}")
        
        # Attempt to reconnect if needed
        if self.should_reconnect:
            print(f"Reconnecting in {self.reconnect_delay} seconds...")
            time.sleep(self.reconnect_delay)
            
            # Exponential backoff for reconnect delay
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
            
            self.connect()
    
    def disconnect(self):
        """Close the WebSocket connection."""
        self.should_reconnect = False
        if self.ws is not None:
            self.ws.close()
        
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        self.connected = False
        print(f"WebSocket connection to {self.exchange} closed")
    
    def is_connected(self):
        """Check if the WebSocket connection is established.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected
