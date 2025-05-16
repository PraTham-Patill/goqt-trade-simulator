# Code Implementation Details

## Overview

This document provides detailed information about the implementation of the Trade Simulator, including key classes, methods, and design decisions.

## Data Layer

### WebSocket Client (`data/websocket_client.py`)

The WebSocket client is responsible for establishing and maintaining connections to exchange WebSocket APIs.

```python
class WebSocketClient:
    def __init__(self, exchange, symbol, callback):
        self.exchange = exchange
        self.symbol = symbol
        self.callback = callback
        self.ws = None
        self.connected = False
        
    def connect(self):
        # Establish WebSocket connection
        # Subscribe to orderbook channel
        # Set up message handlers
        
    def on_message(self, message):
        # Parse incoming message
        # Update orderbook
        # Call callback function
        
    def disconnect(self):
        # Close WebSocket connection
```

### Orderbook (`data/orderbook.py`)

The Orderbook class maintains the current state of the market orderbook and provides methods for analysis.

```python
class Orderbook:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bids = {}  # Price -> Volume mapping
        self.asks = {}  # Price -> Volume mapping
        self.last_update_time = None
        
    def update(self, data):
        # Process orderbook update
        # Update bids and asks
        # Record update time
        
    def get_mid_price(self):
        # Calculate mid price
        
    def get_spread(self):
        # Calculate bid-ask spread
        
    def calculate_slippage(self, size, side):
        # Estimate slippage for given trade size and side
```

## Model Layer

### Almgren-Chriss Model (`models/almgren_chriss.py`)

Implements the Almgren-Chriss market impact model.

```python
class AlmgrenChrissModel:
    def __init__(self, sigma, alpha, lambda_param):
        self.sigma = sigma  # Impact coefficient
        self.alpha = alpha  # Impact exponent
        self.lambda_param = lambda_param  # Risk aversion
        
    def calculate_impact(self, size, volatility, time_horizon):
        # Calculate temporary impact
        temp_impact = self.sigma * (abs(size) ** self.alpha) * (1 if size > 0 else -1)
        
        # Calculate permanent impact
        perm_impact = self.calculate_permanent_impact(size, volatility)
        
        # Calculate total impact
        total_impact = temp_impact + perm_impact + self.lambda_param * (volatility ** 2) * time_horizon
        
        return total_impact
        
    def calculate_permanent_impact(self, size, volatility):
        # Implementation of permanent impact calculation
```

### Slippage Model (`models/slippage.py`)

Calculates expected slippage based on orderbook depth and trade size.

```python
class SlippageModel:
    def __init__(self, orderbook):
        self.orderbook = orderbook
        
    def calculate_slippage(self, size, side):
        # Get relevant side of the orderbook
        book_side = self.orderbook.asks if side == 'buy' else self.orderbook.bids
        
        # Sort price levels
        sorted_levels = sorted(book_side.items(), key=lambda x: x[0], reverse=(side == 'sell'))
        
        # Calculate weighted average price
        remaining_size = size
        total_cost = 0
        
        for price, volume in sorted_levels:
            if remaining_size <= 0:
                break
                
            executed_volume = min(volume, remaining_size)
            total_cost += executed_volume * price
            remaining_size -= executed_volume
            
        # Calculate slippage
        best_price = sorted_levels[0][0] if sorted_levels else 0
        expected_cost = size * best_price
        slippage = (total_cost - expected_cost) / expected_cost if expected_cost > 0 else 0
        
        return slippage
```

### Maker/Taker Model (`models/maker_taker.py`)

Predicts the proportion of orders that will be executed as maker vs. taker.

```python
class MakerTakerModel:
    def __init__(self, orderbook, volatility_window=100):
        self.orderbook = orderbook
        self.volatility_window = volatility_window
        self.price_history = []
        
    def update_price_history(self, price):
        self.price_history.append(price)
        if len(self.price_history) > self.volatility_window:
            self.price_history.pop(0)
            
    def calculate_volatility(self):
        # Calculate price volatility from history
        
    def predict_maker_proportion(self, size, strategy_param):
        # Get current market conditions
        spread = self.orderbook.get_spread()
        volatility = self.calculate_volatility()
        volume = sum(self.orderbook.bids.values()) + sum(self.orderbook.asks.values())
        
        # Predict maker proportion based on market conditions and strategy
        maker_proportion = self.model_function(size, volume, volatility, spread, strategy_param)
        
        return maker_proportion
        
    def model_function(self, size, volume, volatility, spread, strategy_param):
        # Implementation of maker/taker prediction model
```

## UI Layer

### Main Window (`ui/main_window.py`)

The main application window that contains all UI components.

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trade Simulator")
        self.resize(1200, 800)
        
        # Create UI components
        self.input_panel = InputPanel()
        self.output_panel = OutputPanel()
        
        # Set up layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.addWidget(self.input_panel)
        main_layout.addWidget(self.output_panel)
        self.setCentralWidget(main_widget)
        
        # Connect signals and slots
        self.input_panel.parameters_changed.connect(self.update_simulation)
        
        # Initialize data and models
        self.init_data_and_models()
        
    def init_data_and_models(self):
        # Create orderbook
        self.orderbook = Orderbook("BTC-USDT")
        
        # Create WebSocket client
        self.ws_client = WebSocketClient("okx", "BTC-USDT", self.on_orderbook_update)
        self.ws_client.connect()
        
        # Create models
        self.slippage_model = SlippageModel(self.orderbook)
        self.impact_model = AlmgrenChrissModel(0.1, 0.6, 0.1)
        self.maker_taker_model = MakerTakerModel(self.orderbook)
        
    def on_orderbook_update(self, data):
        # Update orderbook
        self.orderbook.update(data)
        
        # Update simulation if needed
        self.update_simulation()
        
    def update_simulation(self):
        # Get parameters from input panel
        params = self.input_panel.get_parameters()
        
        # Calculate results
        slippage = self.slippage_model.calculate_slippage(params['size'], params['side'])
        impact = self.impact_model.calculate_impact(params['size'], params['volatility'], params['time_horizon'])
        maker_proportion = self.maker_taker_model.predict_maker_proportion(params['size'], params['strategy_param'])
        
        # Calculate fees
        maker_fee = 0.0002  # 0.02%
        taker_fee = 0.0005  # 0.05%
        total_fee = params['size'] * (maker_proportion * maker_fee + (1 - maker_proportion) * taker_fee)
        
        # Calculate net cost
        net_cost = slippage + impact + total_fee
        
        # Update output panel
        self.output_panel.update_results({
            'slippage': slippage,
            'impact': impact,
            'maker_proportion': maker_proportion,
            'fee': total_fee,
            'net_cost': net_cost
        })
```

### Input Panel (`ui/input_panel.py`)

Provides controls for adjusting simulation parameters.

```python
class InputPanel(QWidget):
    parameters_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Create UI elements
        self.size_input = QDoubleSpinBox()
        self.side_combo = QComboBox()
        self.strategy_param_input = QSlider(Qt.Horizontal)
        
        # Set up layout
        layout = QVBoxLayout(self)
        # Add UI elements to layout
        
        # Connect signals
        self.size_input.valueChanged.connect(self.parameters_changed)
        self.side_combo.currentIndexChanged.connect(self.parameters_changed)
        self.strategy_param_input.valueChanged.connect(self.parameters_changed)
        
    def get_parameters(self):
        return {
            'size': self.size_input.value(),
            'side': 'buy' if self.side_combo.currentIndex() == 0 else 'sell',
            'strategy_param': self.strategy_param_input.value() / 100.0,
            'volatility': 0.02,  # Default value, could be calculated from market data
            'time_horizon': 60  # Default value in seconds
        }
```

### Output Panel (`ui/output_panel.py`)

Displays simulation results and visualizations.

```python
class OutputPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create UI elements
        self.slippage_label = QLabel("Slippage: 0.00%")
        self.impact_label = QLabel("Market Impact: 0.00%")
        self.maker_taker_label = QLabel("Maker/Taker: 0%/100%")
        self.fee_label = QLabel("Fee: 0.00%")
        self.net_cost_label = QLabel("Net Cost: 0.00%")
        
        # Set up layout
        layout = QVBoxLayout(self)
        # Add UI elements to layout
        
    def update_results(self, results):
        # Update labels with results
        self.slippage_label.setText(f"Slippage: {results['slippage']*100:.2f}%")
        self.impact_label.setText(f"Market Impact: {results['impact']*100:.2f}%")
        self.maker_taker_label.setText(f"Maker/Taker: {results['maker_proportion']*100:.0f}%/{(1-results['maker_proportion'])*100:.0f}%")
        self.fee_label.setText(f"Fee: {results['fee']*100:.2f}%")
        self.net_cost_label.setText(f"Net Cost: {results['net_cost']*100:.2f}%")
```

## Utility Layer

### Configuration (`utils/config.py`)

Manages application settings and parameters.

```python
class Config:
    def __init__(self, config_file=None):
        self.config = {
            'exchange': 'okx',
            'symbol': 'BTC-USDT',
            'impact_coefficient': 0.1,
            'impact_exponent': 0.6,
            'risk_aversion': 0.1,
            'maker_fee': 0.0002,
            'taker_fee': 0.0005,
            'log_level': 'INFO',
            'performance_logging': True
        }
        
        if config_file:
            self.load_from_file(config_file)
            
    def load_from_file(self, config_file):
        # Load configuration from file
        
    def get(self, key, default=None):
        return self.config.get(key, default)
        
    def set(self, key, value):
        self.config[key] = value
```

### Logger (`utils/logger.py`)

Handles application logging and error reporting.

```python
class Logger:
    def __init__(self, log_level='INFO', log_file=None):
        self.log_level = log_level
        self.log_file = log_file
        
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=log_file
        )
        
        self.logger = logging.getLogger('trade_simulator')
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def debug(self, message):
        self.logger.debug(message)
```

### Performance Monitor (`utils/performance.py`)

Tracks and reports on application performance metrics.

```python
class PerformanceMonitor:
    def __init__(self, enabled=True, log_file=None):
        self.enabled = enabled
        self.log_file = log_file
        self.metrics = {}
        self.start_times = {}
        
    def start_timer(self, name):
        if not self.enabled:
            return
            
        self.start_times[name] = time.time()
        
    def stop_timer(self, name):
        if not self.enabled or name not in self.start_times:
            return
            
        elapsed = time.time() - self.start_times[name]
        
        if name not in self.metrics:
            self.metrics[name] = []
            
        self.metrics[name].append(elapsed)
        
        return elapsed
        
    def get_average(self, name):
        if name not in self.metrics or not self.metrics[name]:
            return 0
            
        return sum(self.metrics[name]) / len(self.metrics[name])
        
    def log_metrics(self):
        if not self.enabled or not self.log_file:
            return
            
        with open(self.log_file, 'w') as f:
            f.write('Metric,Average,Min,Max,Count\n')
            
            for name, values in self.metrics.items():
                if not values:
                    continue
                    
                avg = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                count = len(values)
                
                f.write(f'{name},{avg},{min_val},{max_val},{count}\n')
```

This implementation provides a solid foundation for the Trade Simulator, with clean separation of concerns and well-defined interfaces between components.