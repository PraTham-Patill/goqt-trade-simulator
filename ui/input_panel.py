#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Input Panel Module

This module implements the InputPanel class, which provides the UI for configuring
and initiating trade simulations.
"""

import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton,
                             QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QSlider, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from utils.logger import setup_logger


class InputPanel(QWidget):
    """Input panel for configuring and initiating trade simulations."""
    
    # Signal emitted when execution is requested
    execution_requested = pyqtSignal(dict)
    
    def __init__(self):
        """Initialize the input panel."""
        super().__init__()
        
        # Setup logger
        self.logger = setup_logger('input_panel')
        self.logger.info("Initializing input panel")
        
        # Set minimum width
        self.setMinimumWidth(300)
        
        # Setup layout
        self.setup_layout()
        
        self.logger.info("Input panel initialized")
    
    def setup_layout(self):
        """Setup the input panel layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for input fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Create widget for scroll area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tab widget for different model configurations
        tab_widget = QTabWidget()
        
        # Add tabs for different models
        tab_widget.addTab(self.create_almgren_chriss_tab(), "Almgren-Chriss")
        tab_widget.addTab(self.create_slippage_tab(), "Slippage")
        tab_widget.addTab(self.create_maker_taker_tab(), "Maker-Taker")
        
        # Add tab widget to scroll layout
        scroll_layout.addWidget(tab_widget)
        
        # Add common parameters group
        scroll_layout.addWidget(self.create_common_params_group())
        
        # Add execution button
        execute_button = QPushButton("Execute Simulation")
        execute_button.setMinimumHeight(40)
        execute_button.clicked.connect(self.request_execution)
        scroll_layout.addWidget(execute_button)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch(1)
        
        # Set scroll widget as the scroll area's widget
        scroll_area.setWidget(scroll_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
    
    def create_almgren_chriss_tab(self):
        """Create the Almgren-Chriss model configuration tab.
        
        Returns:
            QWidget: The configured tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create form layout for parameters
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Add parameter fields
        self.ac_volatility = QDoubleSpinBox()
        self.ac_volatility.setRange(0.01, 1.0)
        self.ac_volatility.setSingleStep(0.01)
        self.ac_volatility.setValue(0.2)
        self.ac_volatility.setDecimals(2)
        form_layout.addRow("Volatility (annual):", self.ac_volatility)
        
        self.ac_market_impact_permanent = QDoubleSpinBox()
        self.ac_market_impact_permanent.setRange(0.0, 1.0)
        self.ac_market_impact_permanent.setSingleStep(0.001)
        self.ac_market_impact_permanent.setValue(0.1)
        self.ac_market_impact_permanent.setDecimals(3)
        form_layout.addRow("Permanent Market Impact:", self.ac_market_impact_permanent)
        
        self.ac_market_impact_temporary = QDoubleSpinBox()
        self.ac_market_impact_temporary.setRange(0.0, 1.0)
        self.ac_market_impact_temporary.setSingleStep(0.001)
        self.ac_market_impact_temporary.setValue(0.2)
        self.ac_market_impact_temporary.setDecimals(3)
        form_layout.addRow("Temporary Market Impact:", self.ac_market_impact_temporary)
        
        self.ac_risk_aversion = QDoubleSpinBox()
        self.ac_risk_aversion.setRange(0.1, 10.0)
        self.ac_risk_aversion.setSingleStep(0.1)
        self.ac_risk_aversion.setValue(1.0)
        self.ac_risk_aversion.setDecimals(1)
        form_layout.addRow("Risk Aversion:", self.ac_risk_aversion)
        
        # Add form layout to tab layout
        layout.addLayout(form_layout)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
        return tab
    
    def create_slippage_tab(self):
        """Create the Slippage model configuration tab.
        
        Returns:
            QWidget: The configured tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create form layout for parameters
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Add parameter fields
        self.slippage_model = QComboBox()
        self.slippage_model.addItems(["square_root", "linear", "power_law"])
        form_layout.addRow("Slippage Model:", self.slippage_model)
        
        self.slippage_market_impact = QDoubleSpinBox()
        self.slippage_market_impact.setRange(0.01, 1.0)
        self.slippage_market_impact.setSingleStep(0.01)
        self.slippage_market_impact.setValue(0.1)
        self.slippage_market_impact.setDecimals(2)
        form_layout.addRow("Market Impact Factor:", self.slippage_market_impact)
        
        self.slippage_daily_volume = QSpinBox()
        self.slippage_daily_volume.setRange(1000, 10000000)
        self.slippage_daily_volume.setSingleStep(1000)
        self.slippage_daily_volume.setValue(1000000)
        self.slippage_daily_volume.setSuffix(" shares")
        form_layout.addRow("Daily Volume:", self.slippage_daily_volume)
        
        # Add form layout to tab layout
        layout.addLayout(form_layout)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
        return tab
    
    def create_maker_taker_tab(self):
        """Create the Maker-Taker model configuration tab.
        
        Returns:
            QWidget: The configured tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create form layout for parameters
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Add parameter fields
        self.mt_maker_rebate = QDoubleSpinBox()
        self.mt_maker_rebate.setRange(0.0, 50.0)
        self.mt_maker_rebate.setSingleStep(0.1)
        self.mt_maker_rebate.setValue(2.0)
        self.mt_maker_rebate.setDecimals(1)
        self.mt_maker_rebate.setSuffix(" bps")
        form_layout.addRow("Maker Rebate:", self.mt_maker_rebate)
        
        self.mt_taker_fee = QDoubleSpinBox()
        self.mt_taker_fee.setRange(0.0, 50.0)
        self.mt_taker_fee.setSingleStep(0.1)
        self.mt_taker_fee.setValue(3.0)
        self.mt_taker_fee.setDecimals(1)
        self.mt_taker_fee.setSuffix(" bps")
        form_layout.addRow("Taker Fee:", self.mt_taker_fee)
        
        self.mt_spread = QDoubleSpinBox()
        self.mt_spread.setRange(0.1, 100.0)
        self.mt_spread.setSingleStep(0.1)
        self.mt_spread.setValue(5.0)
        self.mt_spread.setDecimals(1)
        self.mt_spread.setSuffix(" bps")
        form_layout.addRow("Spread:", self.mt_spread)
        
        self.mt_fill_probability = QDoubleSpinBox()
        self.mt_fill_probability.setRange(0.01, 1.0)
        self.mt_fill_probability.setSingleStep(0.01)
        self.mt_fill_probability.setValue(0.8)
        self.mt_fill_probability.setDecimals(2)
        form_layout.addRow("Fill Probability:", self.mt_fill_probability)
        
        self.mt_strategy = QComboBox()
        self.mt_strategy.addItems(["taker", "maker", "mixed"])
        form_layout.addRow("Strategy:", self.mt_strategy)
        
        # Add form layout to tab layout
        layout.addLayout(form_layout)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
        return tab
    
    def create_common_params_group(self):
        """Create the common parameters group.
        
        Returns:
            QGroupBox: The configured group box
        """
        group_box = QGroupBox("Common Parameters")
        layout = QVBoxLayout(group_box)
        
        # Create form layout for parameters
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Add parameter fields
        self.model_selector = QComboBox()
        self.model_selector.addItems(["almgren_chriss", "slippage", "maker_taker"])
        form_layout.addRow("Model:", self.model_selector)
        
        self.initial_price = QDoubleSpinBox()
        self.initial_price.setRange(0.01, 10000.0)
        self.initial_price.setSingleStep(0.01)
        self.initial_price.setValue(100.0)
        self.initial_price.setDecimals(2)
        self.initial_price.setPrefix("$")
        form_layout.addRow("Initial Price:", self.initial_price)
        
        self.total_shares = QSpinBox()
        self.total_shares.setRange(100, 1000000)
        self.total_shares.setSingleStep(100)
        self.total_shares.setValue(10000)
        self.total_shares.setSuffix(" shares")
        form_layout.addRow("Total Shares:", self.total_shares)
        
        self.time_horizon = QDoubleSpinBox()
        self.time_horizon.setRange(0.1, 10.0)
        self.time_horizon.setSingleStep(0.1)
        self.time_horizon.setValue(1.0)
        self.time_horizon.setDecimals(1)
        self.time_horizon.setSuffix(" days")
        form_layout.addRow("Time Horizon:", self.time_horizon)
        
        self.num_periods = QSpinBox()
        self.num_periods.setRange(5, 100)
        self.num_periods.setSingleStep(1)
        self.num_periods.setValue(20)
        self.num_periods.setSuffix(" periods")
        form_layout.addRow("Number of Periods:", self.num_periods)
        
        self.is_buy = QCheckBox("Buy Order")
        self.is_buy.setChecked(True)
        form_layout.addRow("", self.is_buy)
        
        # Add form layout to group box layout
        layout.addLayout(form_layout)
        
        return group_box
    
    def request_execution(self):
        """Request execution with the current parameters."""
        self.logger.info("Execution requested")
        
        # Get selected model
        model = self.model_selector.currentText()
        
        # Get common parameters
        params = {
            'model': model,
            'initial_price': self.initial_price.value(),
            'total_shares': self.total_shares.value(),
            'time_horizon': self.time_horizon.value(),
            'num_periods': self.num_periods.value(),
            'is_buy': self.is_buy.isChecked()
        }
        
        # Get model-specific parameters
        if model == 'almgren_chriss':
            params.update({
                'volatility': self.ac_volatility.value(),
                'market_impact_permanent': self.ac_market_impact_permanent.value(),
                'market_impact_temporary': self.ac_market_impact_temporary.value(),
                'risk_aversion': self.ac_risk_aversion.value()
            })
        elif model == 'slippage':
            params.update({
                'slippage_model': self.slippage_model.currentText(),
                'market_impact_factor': self.slippage_market_impact.value(),
                'daily_volume': self.slippage_daily_volume.value()
            })
        elif model == 'maker_taker':
            params.update({
                'maker_rebate': self.mt_maker_rebate.value(),
                'taker_fee': self.mt_taker_fee.value(),
                'spread': self.mt_spread.value(),
                'fill_probability': self.mt_fill_probability.value(),
                'strategy': self.mt_strategy.currentText()
            })
        
        # Emit signal with parameters
        self.execution_requested.emit(params)
    
    def reset(self):
        """Reset all input fields to default values."""
        self.logger.info("Resetting input panel")
        
        # Reset model selector
        self.model_selector.setCurrentIndex(0)
        
        # Reset common parameters
        self.initial_price.setValue(100.0)
        self.total_shares.setValue(10000)
        self.time_horizon.setValue(1.0)
        self.num_periods.setValue(20)
        self.is_buy.setChecked(True)
        
        # Reset Almgren-Chriss parameters
        self.ac_volatility.setValue(0.2)
        self.ac_market_impact_permanent.setValue(0.1)
        self.ac_market_impact_temporary.setValue(0.2)
        self.ac_risk_aversion.setValue(1.0)
        
        # Reset Slippage parameters
        self.slippage_model.setCurrentIndex(0)
        self.slippage_market_impact.setValue(0.1)
        self.slippage_daily_volume.setValue(1000000)
        
        # Reset Maker-Taker parameters
        self.mt_maker_rebate.setValue(2.0)
        self.mt_taker_fee.setValue(3.0)
        self.mt_spread.setValue(5.0)
        self.mt_fill_probability.setValue(0.8)
        self.mt_strategy.setCurrentIndex(0)
