#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Input panel for the Trade Simulator application.

This module implements the input panel of the application, which contains
the input parameters for the trade simulation.
"""

from typing import Dict, Any, Optional, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QGroupBox, QPushButton, QFormLayout,
    QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from loguru import logger

from utils.config import get_available_symbols, get_available_fee_tiers


class InputPanel(QWidget):
    """Input panel containing simulation parameters."""
    
    # Signal emitted when parameters change
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the input panel.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        
        self.config = config
        self.parameters = {}
        
        # Set up the UI
        self._setup_ui()
        
        # Initialize parameters with default values
        self._initialize_parameters()
        
        logger.info("Input panel initialized")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Set panel properties
        self.setMinimumWidth(350)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.setObjectName("input_panel_widget")
        
        # Create main layout with improved spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Add title with improved styling
        title_label = QLabel("Input Parameters")
        title_label.setProperty("title", "true")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Create exchange group with custom styling
        exchange_group = QGroupBox("Exchange Settings")
        exchange_group.setObjectName("exchange_group")
        exchange_layout = QFormLayout()
        exchange_layout.setVerticalSpacing(10)
        exchange_layout.setHorizontalSpacing(15)
        exchange_layout.setContentsMargins(15, 20, 15, 15)
        exchange_group.setLayout(exchange_layout)
        
        # Exchange selection with improved styling
        exchange_label = QLabel("Exchange:")
        exchange_label.setObjectName("form_label")
        self.exchange_combo = QComboBox()
        self.exchange_combo.setObjectName("exchange_combo")
        self.exchange_combo.addItem("OKX")
        self.exchange_combo.setMinimumHeight(30)
        self.exchange_combo.currentTextChanged.connect(self._on_exchange_changed)
        exchange_layout.addRow(exchange_label, self.exchange_combo)
        
        # Symbol selection with improved styling
        symbol_label = QLabel("Spot Asset:")
        symbol_label.setObjectName("form_label")
        self.symbol_combo = QComboBox()
        self.symbol_combo.setObjectName("symbol_combo")
        self.symbol_combo.addItems(get_available_symbols(self.config))
        self.symbol_combo.setMinimumHeight(30)
        self.symbol_combo.currentTextChanged.connect(self._on_symbol_changed)
        exchange_layout.addRow(symbol_label, self.symbol_combo)
        
        main_layout.addWidget(exchange_group)
        
        # Create order group with custom styling
        order_group = QGroupBox("Order Parameters")
        order_group.setObjectName("order_group")
        order_layout = QFormLayout()
        order_layout.setVerticalSpacing(10)
        order_layout.setHorizontalSpacing(15)
        order_layout.setContentsMargins(15, 20, 15, 15)
        order_group.setLayout(order_layout)
        
        # Order type with improved styling
        order_type_label = QLabel("Order Type:")
        order_type_label.setObjectName("form_label")
        self.order_type_combo = QComboBox()
        self.order_type_combo.setObjectName("order_type_combo")
        self.order_type_combo.addItem("Market")
        self.order_type_combo.addItem("Limit")
        self.order_type_combo.setCurrentText("Market")
        self.order_type_combo.setMinimumHeight(30)
        self.order_type_combo.currentTextChanged.connect(self._on_order_type_changed)
        order_layout.addRow(order_type_label, self.order_type_combo)
        
        # Quantity with improved styling
        quantity_label = QLabel("Quantity (~USD):")
        quantity_label.setObjectName("form_label")
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setObjectName("quantity_spin")
        self.quantity_spin.setRange(0.01, 1000000.0)
        self.quantity_spin.setValue(100.0)
        self.quantity_spin.setSuffix(" USD")
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setSingleStep(10.0)
        self.quantity_spin.setMinimumHeight(30)
        self.quantity_spin.valueChanged.connect(self._on_quantity_changed)
        order_layout.addRow(quantity_label, self.quantity_spin)
        
        main_layout.addWidget(order_group)
        
        # Create market parameters group with custom styling
        market_group = QGroupBox("Market Parameters")
        market_group.setObjectName("market_params_group")
        market_layout = QFormLayout()
        market_layout.setVerticalSpacing(10)
        market_layout.setHorizontalSpacing(15)
        market_layout.setContentsMargins(15, 20, 15, 15)
        market_group.setLayout(market_layout)
        
        # Volatility with improved styling
        volatility_label = QLabel("Volatility:")
        volatility_label.setObjectName("form_label")
        self.volatility_spin = QDoubleSpinBox()
        self.volatility_spin.setObjectName("volatility_spin")
        self.volatility_spin.setRange(0.01, 2.0)
        self.volatility_spin.setValue(0.3)
        self.volatility_spin.setSuffix(" (annualized)")
        self.volatility_spin.setDecimals(2)
        self.volatility_spin.setSingleStep(0.05)
        self.volatility_spin.setMinimumHeight(30)
        self.volatility_spin.valueChanged.connect(self._on_volatility_changed)
        market_layout.addRow(volatility_label, self.volatility_spin)
        
        # Fee tier with improved styling
        fee_tier_label = QLabel("Fee Tier:")
        fee_tier_label.setObjectName("form_label")
        self.fee_tier_combo = QComboBox()
        self.fee_tier_combo.setObjectName("fee_tier_combo")
        self.fee_tier_combo.addItems(get_available_fee_tiers(self.config))
        self.fee_tier_combo.setMinimumHeight(30)
        self.fee_tier_combo.currentTextChanged.connect(self._on_fee_tier_changed)
        market_layout.addRow(fee_tier_label, self.fee_tier_combo)
        
        main_layout.addWidget(market_group)
        
        # Add simulate button with improved styling
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 10)
        
        self.simulate_button = QPushButton("Simulate Trade")
        self.simulate_button.setObjectName("simulate_button")
        self.simulate_button.setMinimumHeight(40)
        self.simulate_button.clicked.connect(self._on_simulate_clicked)
        button_layout.addWidget(self.simulate_button)
        
        main_layout.addWidget(button_container)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        logger.debug("Enhanced input panel UI setup complete")
    
    def _initialize_parameters(self) -> None:
        """Initialize parameters with default values."""
        self.parameters = {
            'exchange': self.exchange_combo.currentText(),
            'symbol': self.symbol_combo.currentText(),
            'order_type': self.order_type_combo.currentText().lower(),
            'quantity': self.quantity_spin.value(),
            'volatility': self.volatility_spin.value(),
            'fee_tier': self.fee_tier_combo.currentText(),
        }
        
        # Emit signal with initial parameters
        self.parameters_changed.emit(self.parameters)
        
        logger.debug(f"Parameters initialized: {self.parameters}")
    
    @pyqtSlot(str)
    def _on_exchange_changed(self, exchange: str) -> None:
        """Handle exchange selection change.
        
        Args:
            exchange: Selected exchange
        """
        self.parameters['exchange'] = exchange
        logger.debug(f"Exchange changed to {exchange}")
        self.parameters_changed.emit(self.parameters)
    
    @pyqtSlot(str)
    def _on_symbol_changed(self, symbol: str) -> None:
        """Handle symbol selection change.
        
        Args:
            symbol: Selected symbol
        """
        self.parameters['symbol'] = symbol
        logger.debug(f"Symbol changed to {symbol}")
        self.parameters_changed.emit(self.parameters)
    
    @pyqtSlot(str)
    def _on_order_type_changed(self, order_type: str) -> None:
        """Handle order type selection change.
        
        Args:
            order_type: Selected order type
        """
        self.parameters['order_type'] = order_type.lower()
        logger.debug(f"Order type changed to {order_type}")
        self.parameters_changed.emit(self.parameters)
    
    @pyqtSlot(float)
    def _on_quantity_changed(self, quantity: float) -> None:
        """Handle quantity change.
        
        Args:
            quantity: New quantity value
        """
        self.parameters['quantity'] = quantity
        logger.debug(f"Quantity changed to {quantity}")
        self.parameters_changed.emit(self.parameters)
    
    @pyqtSlot(float)
    def _on_volatility_changed(self, volatility: float) -> None:
        """Handle volatility change.
        
        Args:
            volatility: New volatility value
        """
        self.parameters['volatility'] = volatility
        logger.debug(f"Volatility changed to {volatility}")
        self.parameters_changed.emit(self.parameters)
    
    @pyqtSlot(str)
    def _on_fee_tier_changed(self, fee_tier: str) -> None:
        """Handle fee tier selection change.
        
        Args:
            fee_tier: Selected fee tier
        """
        self.parameters['fee_tier'] = fee_tier
        logger.debug(f"Fee tier changed to {fee_tier}")
        self.parameters_changed.emit(self.parameters)
    
    @pyqtSlot()
    def _on_simulate_clicked(self) -> None:
        """Handle simulate button click."""
        logger.info(f"Simulating trade with parameters: {self.parameters}")
        self.parameters_changed.emit(self.parameters)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get the current parameters.
        
        Returns:
            Dictionary of current parameters
        """
        return self.parameters.copy()
