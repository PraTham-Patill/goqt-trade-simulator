#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Simulator - Main Application Entry Point

This module initializes and runs the Trade Simulator application.
It sets up the UI, data connections, and models.
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

# Import application components
from ui.main_window import MainWindow
from data.websocket_client import WebSocketClient
from data.orderbook import Orderbook
from models.almgren_chriss import AlmgrenChrissModel
from models.slippage import SlippageModel
from models.maker_taker import MakerTakerModel
from utils.config import Config
from utils.logger import Logger
from utils.performance import PerformanceMonitor


def setup_logging():
    """Set up application logging"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logger = Logger(
        log_level='INFO',
        log_file=os.path.join(log_dir, 'trade_simulator.log')
    )
    return logger


def main():
    """Main application entry point"""
    # Set up logging
    logger = setup_logging()
    logger.info("Starting Trade Simulator application")
    
    # Load configuration
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    config = Config(config_file if os.path.exists(config_file) else None)
    
    # Set up performance monitoring
    perf_monitor = PerformanceMonitor(
        enabled=config.get('performance_logging', True),
        log_file=os.path.join('logs', f"performance_{config.get('symbol', 'BTC-USDT')}_{config.get('exchange', 'okx')}.csv")
    )
    
    # Initialize QApplication
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = MainWindow(config, logger, perf_monitor)
    main_window.show()
    
    # Start application event loop
    exit_code = app.exec_()
    
    # Clean up resources
    logger.info("Shutting down Trade Simulator application")
    perf_monitor.log_metrics()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
