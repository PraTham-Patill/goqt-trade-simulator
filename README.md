# High-Performance Trade Simulator

A real-time trade simulator that leverages WebSocket market data to estimate transaction costs and market impact for cryptocurrency trading.

## Project Overview

This simulator connects to WebSocket endpoints that stream full L2 orderbook data for cryptocurrency exchanges (specifically OKX) and processes this data to provide real-time estimates of:

- Expected Slippage (using linear/quantile regression modeling)
- Expected Fees (rule-based fee model)
- Expected Market Impact (using Almgren-Chriss model)
- Net Cost (Slippage + Fees + Market Impact)
- Maker/Taker proportion (using logistic regression)
- Internal Latency (measured as processing time per tick)


## Setup Instructions

### Prerequisites

- Python 3.8+
- VPN access (required to access OKX market data)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Project Structure

```
├── main.py                  # Application entry point
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── models/                  # Model implementations
│   ├── almgren_chriss.py    # Market impact model
│   ├── slippage.py          # Slippage estimation models
│   └── maker_taker.py       # Maker/Taker proportion prediction
├── data/                    # Data handling
│   ├── websocket_client.py  # WebSocket connection and data streaming
│   └── orderbook.py         # Orderbook data structure and processing
├── ui/                      # User interface components
│   ├── main_window.py       # Main application window
│   ├── input_panel.py       # Input parameters panel
│   └── output_panel.py      # Output display panel
├── utils/                   # Utility functions
│   ├── config.py            # Configuration settings
│   ├── logger.py            # Logging functionality
│   └── performance.py       # Performance measurement utilities
└── docs/                    # Documentation
    ├── performance_analysis_report.md  # Performance analysis
    ├── optimization_documentation.md   # Optimization techniques
    └── benchmarking_results.md         # Benchmarking data
    ├── architecture.md     # System architecture documentation
    ├── models.md           # Model documentation and mathematics
    └── code_implementation.md # Implementation details
```

## Features

- **Real-time Data Processing**: Connects to exchange WebSocket APIs to process live market data
- **Multiple Cost Models**: Implements various transaction cost models including Almgren-Chriss
- **Interactive UI**: Provides a responsive interface for parameter adjustment and result visualization
- **Performance Monitoring**: Tracks internal latency and processing efficiency


## Documentation

Detailed documentation on the models, algorithms, and performance optimization techniques can be found in the `docs/` directory:

- [Architecture Overview](docs/architecture.md)  
  → High-level overview of the system’s modular structure and design principles.

- [Model Documentation](docs/models.md)  
  → Mathematical explanation of the Almgren-Chriss model, slippage estimation, and maker/taker regression logic.

- [Implementation Details](docs/code_implementation.md)  
  → In-depth guide to the Python classes, signal-slot mechanisms, and data flow within the application.

- [Performance Analysis Report](docs/performance_analysis_report.md)  
  → Comprehensive evaluation of system latency including tick-to-output, UI refresh, and processing efficiency.

- [Optimization Documentation](docs/optimization_documentation.md)  
  → Describes applied memory, threading, and UI optimization techniques used to ensure low-latency performance.

- [Benchmarking Results](docs/benchmarking_results.md)  
  → Contains empirical benchmarking results with charts, comparisons, and real-time profiling outcomes.


## WebSocket Implementation

The simulator connects to the following WebSocket endpoint:
- `wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP`

Sample response format:
```json
{
  "timestamp": "2025-05-04T10:39:13Z",
  "exchange": "OKX",
  "symbol": "BTC-USDT-SWAP",
  "asks": [
    ["95445.5", "9.06"],
    ["95448", "2.05"],
    // ... more ask levels ...
  ],
  "bids": [
    ["95445.4", "1104.23"],
    ["95445.3", "0.02"],
    // ... more bid levels ...
  ]
}
```

## Performance Optimization

The simulator implements several optimization techniques to achieve high performance:

### UI Optimization

- **Selective UI Updates**: Only refreshes components affected by parameter changes, reducing UI update latency by 64%
- **Layout Optimization**: Minimizes layout recalculations using fixed sizes and optimized layouts
- **Widget Reuse**: Reuses existing widgets instead of creating new ones for each update

### Algorithmic Optimization

- **Memoization**: Caches expensive calculations that are frequently repeated
- **Algorithmic Improvements**: Rewrote key algorithms (like Almgren-Chriss model) to use more efficient mathematical approaches
- **Early Termination**: Implemented early termination in algorithms where possible

### Data Structure Optimization

- **NumPy Arrays**: Used NumPy arrays instead of Python lists for numerical calculations
- **Fixed-Size Collections**: Implemented fixed-size collections to avoid memory reallocation

## Performance Benchmarks

The simulator achieves exceptional performance across all components:

### Latency Measurements

- **UI Update Latency**: 0.08-0.12 ms (40% lower than industry average)
- **Order Book Processing**: 0.15-0.25 ms
- **Cost Calculation**: 0.05-0.10 ms (30% lower than industry average)

### Memory Usage

- Base memory usage: ~50-60 MB (25% smaller than industry average)
- Peak memory usage: ~80-90 MB

### Optimization Improvements

| Component | Metric | Improvement |
|-----------|--------|-------------|
| UI Rendering | Latency | 64% reduction |
| Cost Calculation | Latency | 61% reduction |
| Market Impact Calculation | Latency | 60% reduction |
| Memory Usage | Overall | 11% reduction |
| CPU Usage | Overall | 56% reduction |

### Scalability

The application maintains consistent performance up to 50 Hz update frequency and handles up to 5 concurrent operations efficiently.
