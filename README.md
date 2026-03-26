# GNPy.app Scraper

A Python web scraper that extracts transceiver specifications from [GNPy.app](https://gnpy.app/) - an optical network simulation tool.

## Overview

This tool automatically scrapes transceiver parameters for all available transceiver types and modes from GNPy.app, including:

- **Margin (dB)** - System margin
- **Baudrate (Gbaud)** - Symbol rate
- **Roll-off** - Pulse shaping factor
- **Tx OSNR (dB)** - Transmitter optical signal-to-noise ratio
- **Min OSNR (dB)** - Minimum required OSNR

## Installation

### Prerequisites

- Python 3.8+
- Playwright browser automation

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gnpy-scraper.git
cd gnpy-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

Run the scraper:

```bash
python app.py
```

The script will:
1. Open a browser window (non-headless for visibility)
2. Navigate to GNPy.app
3. Iterate through all transceiver types and modes
4. Extract parameter values for each combination
5. Save results to `gnpy_results.csv`

### Output

Results are saved to `gnpy_results.csv` with columns:

| Column | Description |
|--------|-------------|
| transceiver | Transceiver type name |
| mode | Operating mode |
| Margin_dB | System margin in dB |
| Baudrate_Gbaud | Baudrate in Gbaud |
| Roll_off | Roll-off factor |
| Tx_OSNR_dB | Transmitter OSNR in dB |
| Min_OSNR_dB | Minimum required OSNR in dB |

### Example Output

```csv
transceiver,mode,Margin_dB,Baudrate_Gbaud,Roll_off,Tx_OSNR_dB,Min_OSNR_dB
OpenZR+,400ZR+ DP-16QAM,3.0,60.14,0.15,38,26.5
OIF 400ZR,400 Gbit/s DP-16QAM,3.0,59.84,0.15,38,26.5
```

## Configuration

To run in headless mode (no visible browser), modify `app.py`:

```python
browser = p.chromium.launch(headless=True)  # Change to True
```

## Technical Details

- Uses **Playwright** for browser automation
- Handles **ReactVirtualized** dropdowns by scrolling to load all options
- Extracts values directly from DOM using JavaScript evaluation
- Supports React-Select dropdown components

## Supported Transceivers

The scraper automatically discovers all available transceivers including:
- OpenZR+
- OIF 400ZR
- OpenROADM MSA ver. 4.0 / 5.0
- CableLabs P2PCO
- IEEE
- Voyager
- Smartoptics QSFP-DD/QSFP28 variants
- And more...

## License

MIT License - see [LICENSE](LICENSE) file.

## Disclaimer

This tool is for educational and research purposes. Please respect GNPy.app's terms of service and use responsibly.

## Credits

- [GNPy](https://github.com/Telecominfraproject/oopt-gnpy) - Open Optical Network Planning library
- [GNPy.app](https://gnpy.app/) - Web interface for GNPy simulations
