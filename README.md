# High-Performance Trade Simulator

A real-time trade simulator that leverages WebSocket market data to estimate transaction costs and market impact for cryptocurrency trading.

## Project Overview

This simulator connects to WebSocket endpoints that stream full L2 orderbook data for cryptocurrency exchanges (specifically OKX) and processes this data to provide real-time estimates of:

- Expected Slippage
- Expected Fees
- Expected Market Impact (using Almgren-Chriss model)
- Net Cost
- Maker/Taker proportion
- Internal Latency

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
├── README.md               # Project documentation
├── models/                 # Model implementations
│   ├── almgren_chriss.py   # Market impact model
│   ├── slippage.py         # Slippage estimation models
│   └── maker_taker.py      # Maker/Taker proportion prediction
├── data/                   # Data handling
│   ├── websocket_client.py # WebSocket connection and data streaming
│   └── orderbook.py        # Orderbook data structure and processing
├── ui/                     # User interface components
│   ├── main_window.py      # Main application window
│   ├── input_panel.py      # Input parameters panel
│   ├── output_panel.py     # Results display panel
│   └── style.py            # UI styling and themes
├── utils/                  # Utility functions
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging functionality
│   └── performance.py      # Performance monitoring
└── docs/                   # Documentation
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

Detailed documentation is available in the `docs/` directory:

- [Architecture Overview](docs/architecture.md)
- [Model Documentation](docs/models.md)
- [Implementation Details](docs/code_implementation.md)

## Submission Guidelines

Please refer to the [Submission Guide](docs/submission_guide.md) and [Submission Checklist](docs/submission_checklist.md) for details on how to submit your completed assignment.

## License

This project is proprietary and confidential. All rights reserved.