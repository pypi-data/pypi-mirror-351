# AWS EventBridge Explorer

> *Where Events Meet Clarity*

This tool helps you visualize AWS EventBridge event buses and their rules as an interactive graph.

## Features

- Lists all AWS EventBridge event buses in your account
- Allows you to select an event bus
- Fetches all rules associated with the selected event bus
- Creates an interactive visual graph showing the relationships between:
  - Event bus
  - Rules
  - Rule targets
- Touch or click on nodes to view detailed information
- Modern, touch-friendly UI for better exploration and analysis
- Filter and select specific rules to display
- View recent logs and event payloads for rules

## Installation

### From PyPI (Recommended)

```bash
pip install aws-eventbridge-explorer
```

### Using uvx (No Installation Required)

Run directly without installing using `uvx`:

```bash
uvx --from aws-eventbridge-explorer eventbridge-explorer
```

With a specific AWS profile:

```bash
AWS_PROFILE=your-profile uvx --from aws-eventbridge-explorer eventbridge-explorer
```

### From Source

```bash
git clone https://github.com/glyphtek/aws-eventbridge-explorer.git
cd aws-eventbridge-explorer
pip install -e .
```

## Requirements

- Python 3.8+
- AWS CLI configured with appropriate permissions
- Required Python packages (installed automatically when using pip)

## Usage

### Basic Usage

Run the application with the web interface:

```bash
eventbridge-explorer
```

### With Custom Port

```bash
eventbridge-explorer --port 8080
```

### With Specific AWS Profile

```bash
AWS_PROFILE=your-profile eventbridge-explorer
```

### Using uvx (No Installation)

```bash
# Basic usage
uvx --from aws-eventbridge-explorer eventbridge-explorer

# With specific AWS profile
AWS_PROFILE=your-profile uvx --from aws-eventbridge-explorer eventbridge-explorer

# With custom port
uvx --from aws-eventbridge-explorer eventbridge-explorer --port 8080
```

### Legacy Method (main.py)

You can also run using the main.py file:

```bash
python main.py
```

You can also specify a custom port:

```bash
python main.py --port 8080
```

Once running, open your browser and navigate to `http://localhost:5050` (or the port you specified).

## Project Structure

```
eventbridge/
├── __init__.py     # Package initialization
├── core.py         # Core functionality and AWS interactions
├── web_server.py   # Flask web server implementation
└── static/         # Static web assets (CSS, JS, etc.)
    └── templates/  # HTML templates
main.py             # Main entry point
requirements.txt    # Dependencies
```

## UI Features

- Left panel: Select event buses and view detailed information
- Right panel: Interactive graph visualization
- Touch or click on any node (event bus, rule, or target) to view its details
- Filter and select specific rules to display
- Fetch and view recent logs and event payloads for rules
- Send test events to EventBridge that match rule patterns

## Graph Interpretation

- **Dark gray node**: Event bus 
- **Light blue nodes**: Rules
- **Soft yellow nodes**: Lambda targets 
- **Lavender nodes**: SQS service targets
- **Mint green nodes**: SNS service targets
- **Arrows**: Show the flow of events from the event bus to rules to targets

### Development Mode

1. In a separate terminal, start the Flask application:

```bash
python main.py
```