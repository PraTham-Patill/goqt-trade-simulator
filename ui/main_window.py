#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window Module

This module implements the main application window for the GoQuant Trade Simulator.
It integrates all UI components and handles the overall application layout.
"""

import sys
import time
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QSplitter, QTabWidget, QLabel,
                             QStatusBar, QMenuBar, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from ui.input_panel import InputPanel
from ui.output_panel import OutputPanel
from ui.style import apply_stylesheet
from utils.logger import setup_logger
from utils.performance import PerformanceMonitor


class MainWindow(QMainWindow):
    """Main application window for the GoQuant Trade Simulator."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Setup logger
        self.logger = setup_logger('main_window')
        self.logger.info("Initializing main window")
        
        # Setup performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize UI
        self.setWindowTitle("GoQuant Trade Simulator")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Apply stylesheet
        apply_stylesheet(self)
        
        # Setup central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Setup layout
        self.setup_layout()
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Setup timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # Update every 100ms
        
        self.logger.info("Main window initialized")
    
    def setup_layout(self):
        """Setup the main window layout."""
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Create input panel
        self.input_panel = InputPanel()
        self.input_panel.execution_requested.connect(self.handle_execution_request)
        
        # Create output panel
        self.output_panel = OutputPanel()
        
        # Add panels to splitter
        self.splitter.addWidget(self.input_panel)
        self.splitter.addWidget(self.output_panel)
        
        # Set initial sizes
        self.splitter.setSizes([400, 800])
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
    
    def setup_menu_bar(self):
        """Setup the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New simulation action
        new_action = QAction("&New Simulation", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_simulation)
        file_menu.addAction(new_action)
        
        # Save results action
        save_action = QAction("&Save Results", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_results)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        # Toggle performance monitor action
        perf_action = QAction("&Performance Monitor", self)
        perf_action.setCheckable(True)
        perf_action.setChecked(False)
        perf_action.triggered.connect(self.toggle_performance_monitor)
        view_menu.addAction(perf_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def new_simulation(self):
        """Reset the application for a new simulation."""
        self.logger.info("Starting new simulation")
        self.input_panel.reset()
        self.output_panel.reset()
        self.status_bar.showMessage("New simulation started")
    
    def save_results(self):
        """Save the simulation results."""
        self.logger.info("Saving results")
        self.output_panel.save_results()
        self.status_bar.showMessage("Results saved")
    
    def toggle_performance_monitor(self, checked):
        """Toggle the performance monitor display."""
        if checked:
            self.performance_monitor.start()
            self.status_bar.showMessage("Performance monitoring enabled")
        else:
            self.performance_monitor.stop()
            self.status_bar.showMessage("Performance monitoring disabled")
    
    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About GoQuant Trade Simulator",
            "<h3>GoQuant Trade Simulator</h3>"
            "<p>Version 1.0</p>"
            "<p>A sophisticated trading simulator for algorithmic execution strategies.</p>"
            "<p>© 2023 GoQuant</p>"
        )
    
    def handle_execution_request(self, params):
        """Handle execution request from the input panel.
        
        Args:
            params (dict): Execution parameters
        """
        self.logger.info(f"Execution requested with params: {params}")
        self.status_bar.showMessage("Executing simulation...")
        
        # Start performance monitoring for this execution
        self.performance_monitor.start_execution()
        
        # Simulate execution (in a real application, this would be done in a separate thread)
        # For demonstration, we'll just add a small delay
        time.sleep(0.1)
        
        # Generate some sample results
        results = self.generate_sample_results(params)
        
        # Stop performance monitoring
        execution_time = self.performance_monitor.stop_execution()
        
        # Update output panel with results
        self.output_panel.update_results(results, execution_time)
        
        self.status_bar.showMessage(f"Execution completed in {execution_time:.2f} seconds")
    
    def generate_sample_results(self, params):
        """Generate sample results for demonstration.
        
        Args:
            params (dict): Execution parameters
        
        Returns:
            dict: Sample results
        """
        # Extract parameters
        model = params.get('model', 'almgren_chriss')
        initial_price = params.get('initial_price', 100.0)
        total_shares = params.get('total_shares', 10000)
        time_horizon = params.get('time_horizon', 1.0)
        num_periods = params.get('num_periods', 20)
        
        # Generate time points
        times = np.linspace(0, time_horizon * 6.5 * 3600, num_periods + 1) / 3600  # Convert to hours
        
        # Generate sample execution trajectory
        if model == 'almgren_chriss':
            # Linear trajectory for simplicity
            shares_remaining = np.linspace(total_shares, 0, num_periods + 1)
            execution_sizes = np.diff(np.append(total_shares, shares_remaining))
            
            # Generate sample prices with some random walk
            volatility = params.get('volatility', 0.2) / np.sqrt(252 * 6.5 * 3600)  # Per-second volatility
            price_path = np.zeros(num_periods + 1)
            price_path[0] = initial_price
            
            for i in range(1, num_periods + 1):
                price_change = np.random.normal(0, volatility * np.sqrt(time_horizon * 6.5 * 3600 / num_periods))
                price_path[i] = price_path[i-1] + price_change
        
        else:  # Default fallback
            shares_remaining = np.linspace(total_shares, 0, num_periods + 1)
            execution_sizes = np.diff(np.append(total_shares, shares_remaining))
            price_path = np.linspace(initial_price, initial_price * 1.01, num_periods + 1)
        
        # Calculate execution prices (with some slippage)
        execution_prices = price_path[1:] - 0.01 * execution_sizes / 1000
        
        # Calculate VWAP and implementation shortfall
        vwap = np.sum(execution_sizes * execution_prices) / total_shares
        shortfall = (initial_price - vwap) * total_shares
        
        # Create results dictionary
        results = {
            'model': model,
            'times': times,
            'shares_remaining': shares_remaining,
            'execution_sizes': np.append(execution_sizes, 0),  # Add 0 for the last period
            'price_path': price_path,
            'execution_prices': np.append(execution_prices, 0),  # Add 0 for the last period
            'vwap': vwap,
            'shortfall': shortfall,
            'params': params
        }
        
        return results
    
    def update_ui(self):
        """Update UI components."""
        # This method is called periodically by the timer
        # In a real application, this would update real-time data displays
        pass
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        self.performance_monitor.save_metrics()
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
