#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Output panel for the Trade Simulator application.

This module implements the output panel of the application, which displays
the simulation results and performance metrics.
"""

from typing import Dict, Any, Optional, List
import time

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QFormLayout, QSizePolicy, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPalette
from loguru import logger

from models.almgren_chriss import AlmgrenChrissModel
from models.slippage import create_slippage_model
from models.maker_taker import MakerTakerModel
from utils.config import get_fee_tier


class OutputPanel(QWidget):
    """Output panel displaying simulation results."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the output panel.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        
        self.config = config
        self.parameters = {}
        self.orderbook_data = {}
        self.last_update_time = 0.0
        
        # Initialize models
        self.almgren_chriss_model = AlmgrenChrissModel(config)
        self.slippage_model = create_slippage_model(config)
        self.maker_taker_model = MakerTakerModel(config)
        
        # Set up the UI
        self._setup_ui()
        
        logger.info("Output panel initialized")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Set panel properties
        self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Add title
        title_label = QLabel("Simulation Results")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Create market data group with styled box
        market_group = QGroupBox("Market Data")
        market_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f8f9fa;
                color: #3498db;
            }
        """)
        market_layout = QFormLayout()
        market_layout.setVerticalSpacing(10)
        market_layout.setHorizontalSpacing(15)
        market_group.setLayout(market_layout)
        
        # Create label styles
        label_style = "font-size: 13px; font-weight: bold; color: #34495e;"
        self.value_style = "font-size: 13px; color: #2c3e50; padding: 5px; background-color: #f8f9fa; border-radius: 4px;"
        
        # Market data labels
        exchange_title = QLabel("Exchange:")
        exchange_title.setStyleSheet(label_style)
        self.exchange_label = QLabel("--")
        self.exchange_label.setStyleSheet(self.value_style)
        market_layout.addRow(exchange_title, self.exchange_label)
        
        symbol_title = QLabel("Symbol:")
        symbol_title.setStyleSheet(label_style)
        self.symbol_label = QLabel("--")
        self.symbol_label.setStyleSheet(self.value_style)
        market_layout.addRow(symbol_title, self.symbol_label)
        
        price_title = QLabel("Current Price:")
        price_title.setStyleSheet(label_style)
        self.price_label = QLabel("--")
        self.price_label.setStyleSheet(self.value_style + "; font-weight: bold;")
        market_layout.addRow(price_title, self.price_label)
        
        spread_title = QLabel("Spread:")
        spread_title.setStyleSheet(label_style)
        self.spread_label = QLabel("--")
        self.spread_label.setStyleSheet(self.value_style)
        market_layout.addRow(spread_title, self.spread_label)
        
        liquidity_title = QLabel("Liquidity Imbalance:")
        liquidity_title.setStyleSheet(label_style)
        self.liquidity_label = QLabel("--")
        self.liquidity_label.setStyleSheet(self.value_style)
        market_layout.addRow(liquidity_title, self.liquidity_label)
        
        main_layout.addWidget(market_group)
        
        # Create cost estimation group
        cost_group = QGroupBox("Cost Estimation")
        cost_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f8f9fa;
                color: #e74c3c;
            }
        """)
        cost_layout = QFormLayout()
        cost_layout.setVerticalSpacing(10)
        cost_layout.setHorizontalSpacing(15)
        cost_group.setLayout(cost_layout)
        
        # Cost estimation labels with enhanced styling
        slippage_title = QLabel("Expected Slippage:")
        slippage_title.setStyleSheet(label_style)
        self.slippage_label = QLabel("--")
        self.slippage_label.setStyleSheet(self.value_style)
        cost_layout.addRow(slippage_title, self.slippage_label)
        
        fees_title = QLabel("Expected Fees:")
        fees_title.setStyleSheet(label_style)
        self.fees_label = QLabel("--")
        self.fees_label.setStyleSheet(self.value_style)
        cost_layout.addRow(fees_title, self.fees_label)
        
        impact_title = QLabel("Expected Market Impact:")
        impact_title.setStyleSheet(label_style)
        self.impact_label = QLabel("--")
        self.impact_label.setStyleSheet(self.value_style)
        cost_layout.addRow(impact_title, self.impact_label)
        
        net_cost_title = QLabel("Net Cost:")
        net_cost_title.setStyleSheet(label_style)
        self.net_cost_label = QLabel("--")
        self.net_cost_label.setStyleSheet(self.value_style + "; font-weight: bold; color: #e74c3c;")
        cost_layout.addRow(net_cost_title, self.net_cost_label)
        
        maker_taker_title = QLabel("Maker/Taker Proportion:")
        maker_taker_title.setStyleSheet(label_style)
        self.maker_taker_label = QLabel("--")
        self.maker_taker_label.setStyleSheet(self.value_style)
        cost_layout.addRow(maker_taker_title, self.maker_taker_label)
        
        main_layout.addWidget(cost_group)
        
        # Create performance group
        perf_group = QGroupBox("Performance Metrics")
        perf_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f8f9fa;
                color: #2ecc71;
            }
        """)
        perf_layout = QFormLayout()
        perf_layout.setVerticalSpacing(10)
        perf_layout.setHorizontalSpacing(15)
        perf_group.setLayout(perf_layout)
        
        # Performance metrics labels with enhanced styling
        latency_title = QLabel("Processing Latency:")
        latency_title.setStyleSheet(label_style)
        self.latency_label = QLabel("--")
        self.latency_label.setStyleSheet(self.value_style)
        perf_layout.addRow(latency_title, self.latency_label)
        
        update_title = QLabel("UI Update Time:")
        update_title.setStyleSheet(label_style)
        self.update_label = QLabel("--")
        self.update_label.setStyleSheet(self.value_style)
        perf_layout.addRow(update_title, self.update_label)
        
        main_layout.addWidget(perf_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        logger.debug("Enhanced output panel UI setup complete")
    
    def update_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update the panel with new parameters.
        
        Args:
            parameters: Dictionary of updated parameters
        """
        self.parameters = parameters.copy()
        
        # Update UI elements with parameter values
        self.exchange_label.setText(parameters.get('exchange', '--'))
        self.symbol_label.setText(parameters.get('symbol', '--'))
        
        # Calculate and update cost estimates
        self._update_cost_estimates()
        
        logger.debug(f"Output panel updated with parameters: {parameters}")
    
    def update_orderbook_data(self, data: Dict[str, Any]) -> None:
        """Update the panel with new orderbook data.
        
        Args:
            data: Dictionary of orderbook data
        """
        self.orderbook_data = data.copy()
        self.last_update_time = time.time()
        
        # Update market data display
        if 'best_bid' in data and 'best_ask' in data:
            mid_price = (data['best_bid'] + data['best_ask']) / 2
            self.price_label.setText(f"${mid_price:.2f}")
            
            spread = data['best_ask'] - data['best_bid']
            spread_bps = (spread / mid_price) * 10000
            self.spread_label.setText(f"{spread_bps:.1f} bps (${spread:.2f})")
            
            # Calculate liquidity imbalance (bid vs ask volume)
            if 'bid_volume' in data and 'ask_volume' in data:
                total_volume = data['bid_volume'] + data['ask_volume']
                if total_volume > 0:
                    bid_pct = (data['bid_volume'] / total_volume) * 100
                    self.liquidity_label.setText(f"{bid_pct:.1f}% bid / {100-bid_pct:.1f}% ask")
        
        # Update performance metrics
        if 'processing_latency' in data:
            self.latency_label.setText(f"{data['processing_latency']:.2f} ms")
        
        # Recalculate cost estimates with new market data
        self._update_cost_estimates()
        
        logger.debug("Output panel updated with orderbook data")
    
    def update_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update the performance metrics display.
        
        Args:
            metrics: Dictionary of performance metrics
        """
        # Update UI update time
        if 'ui_update' in metrics and 'mean' in metrics['ui_update']:
            self.update_label.setText(f"{metrics['ui_update']['mean']:.2f} ms")
        
        logger.debug("Performance metrics updated")
    
    def _update_cost_estimates(self) -> None:
        """Update the cost estimation displays based on current parameters and market data."""
        # Skip if we don't have necessary parameters
        if not self.parameters or 'quantity' not in self.parameters:
            return
        
        # Get parameters
        quantity = self.parameters.get('quantity', 0.0)
        order_type = self.parameters.get('order_type', 'market')
        fee_tier = self.parameters.get('fee_tier', 'retail')
        
        # Get current price from orderbook data or use default
        current_price = 0.0
        if 'best_bid' in self.orderbook_data and 'best_ask' in self.orderbook_data:
            current_price = (self.orderbook_data['best_bid'] + self.orderbook_data['best_ask']) / 2
        else:
            # Use a default price if no orderbook data available
            current_price = 100.0
        
        # Calculate expected slippage
        slippage = 0.0
        if order_type == 'market':
            # Simple slippage model: 0.1% for market orders
            slippage = quantity * current_price * 0.001
        self.slippage_label.setText(f"${slippage:.2f} ({(slippage / (quantity * current_price) * 100):.2f}%)")
        
        # Calculate expected fees
        fee_rate = get_fee_tier(self.config, fee_tier)
        fees = quantity * current_price * fee_rate
        self.fees_label.setText(f"${fees:.2f} ({fee_rate * 100:.3f}%)")
        
        # Calculate expected market impact
        impact = 0.0
        if quantity > 1000:
            # Simple market impact model: 0.1% per $1000 for large orders
            impact = quantity * current_price * 0.001 * (quantity / 1000)
        self.impact_label.setText(f"${impact:.2f} ({(impact / (quantity * current_price) * 100):.2f}%)")
        
        # Calculate net cost
        net_cost = slippage + fees + impact
        net_cost_pct = (net_cost / (quantity * current_price)) * 100
        self.net_cost_label.setText(f"${net_cost:.2f} ({net_cost_pct:.2f}%)")
        
        # Update maker/taker proportion
        if order_type == 'market':
            self.maker_taker_label.setText("100% Taker")
        elif order_type == 'limit':
            self.maker_taker_label.setText("100% Maker")
        
        logger.debug("Cost estimates updated")
