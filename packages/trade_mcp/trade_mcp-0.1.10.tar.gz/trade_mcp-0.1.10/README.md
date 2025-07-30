# Trade MCP Server

## Overview

Trade MCP Server provides a unified interface to interact with Binance Futures (Testnet) and Aster (Mainnet) APIs using the Multi-Channel Protocol (MCP). It exposes a rich set of trading, account, and market data tools, and is designed for integration with MCP clients such as Cursor or Claude Desktop.

- Supports both Binance (Testnet) and Aster (Mainnet) via a single server.
- Exposes trading, account, and market data tools as MCP commands.
- Easily configurable for local or remote use.
- **Gateway now records usage by reading and writing to a single JSON file on Google Cloud Run.**

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (a fast Python package manager, recommended for setup)
- Your API key and secret for either Aster or Binance Testnet

### 2. Installation

Clone the repository and install dependencies using `uv`:

```bash
git clone <repository_url>
cd trade_mcp
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

> If you don't have `uv` installed, get it with:
> ```bash
> pip install uv
> ```

---

## Usage

You can run the MCP server locally using the provided CLI. The server exposes all MCP tools over stdio for integration with MCP clients.

### Start the Server

Refer to the [Running Modes and Venue Parameter](#running-modes-and-venue-parameter) section below to select the appropriate mode for your use case. Choose the correct keys and set the `--venue` parameter as needed.

#### Example (Debug Mode)
```bash
trade-mcp-serve --api-key <YOUR_BN_KEY> --api-secret <YOUR_BN_SECRET> --axgrad-key <YOUR_AXGRAD_KEY> --venue="test"
```

#### Example (Competition Mode)
```bash
trade-mcp-serve --axgrad-key <YOUR_AXGRAD_KEY> --venue="axgrad_game_1"
```

#### Example (Live Trading)
```bash
trade-mcp-serve --api-key <YOUR_ASTER_KEY> --api-secret <YOUR_ASTER_SECRET> --venue="live"
```

---

## Running Modes and Venue Parameter

Depending on your use case, you will need to provide different keys and set the `--venue` parameter accordingly:

### 1. Pre-competition Debugging (Gateway, BN key + AxGradKey, default `--venue="test"`)
- **Purpose:** For pre-competition debugging and validation (users must complete at least 5 debug trades).
- **Keys Required:** Binance (BN) key, AxGradKey
- **Venue:** `test` (default)
- **Gateway:** Used
- **Example:**
  ```bash
  trade-mcp-serve --api-key <YOUR_BN_KEY> --api-secret <YOUR_BN_SECRET> --axgrad-key <YOUR_AXGRAD_KEY> --venue="test"
  ```

### 2. Competition Mode (Gateway, AxGradKey, `--venue="axgrad_game_1"`)
- **Purpose:** For official competition participation.
- **Keys Required:** AxGradKey
- **Venue:** `axgrad_game_1`
- **Gateway:** Used
- **Note:** The `axgrad_game_1` venue is only available after the official launch time. If you attempt to use this venue before launch, you will receive an error indicating the Axgrad game is not yet available.
- **Example:**
  ```bash
  trade-mcp-serve --axgrad-key <YOUR_AXGRAD_KEY> --venue="axgrad_game_1"
  ```

### 3. Live Trading (Direct, Aster key, `--venue="live"`)
- **Purpose:** For real trading (live), bypassing the gateway.
- **Keys Required:** Aster key
- **Venue:** `live`
- **Gateway:** Not used
- **Example:**
  ```bash
  trade-mcp-serve --api-key <YOUR_ASTER_KEY> --api-secret <YOUR_ASTER_SECRET> --venue="live"
  ```

> **Note:**
> - The `--venue` parameter defaults to `test` if not specified.
> - Make sure to use the correct key and venue combination for your intended use case.

---

## MCP Client Integration

### Cursor Example

Add the following to your `~/.cursor/mcp.json`:

```json
{
  "binance-mcp-server-local": {
    "command": "uvx",
    "args": [
      "--from",
      "trade_mcp",
      "trade-mcp-serve",
      "--axgrad-key",
      "<YOUR_AXGRAD_KEY>"
    ]
  }
}
```

- Adjust the arguments as needed for your environment.

---

## Available MCP Tools

The server exposes a wide range of tools, including:

- Account and position management (`get_account_info`, `get_balance`, `get_position_mode`, etc.)
- Order management (`place_order`, `cancel_order`, `get_open_orders`, etc.)
- Market data (`get_order_book`, `get_klines`, `get_mark_price`, etc.)

See `src/trade_mcp/server/mcp_tools.py` for the full list and details.

---

## Detailed MCP Tool Descriptions

### Account and Position Management

- **get_account_info**  
  Get account information including balances and open positions.

- **get_balance**  
  Get the current futures account balance.

- **get_position_mode**  
  Get the user's position mode (Hedge Mode or One-way Mode).

- **change_position_mode**  
  Change position mode between Hedge Mode and One-way Mode.  
  Args:  
  - `dual_side`: `"true"` for Hedge Mode, `"false"` for One-way Mode

- **get_position_info**  
  Get current position information for a symbol or all symbols.

- **modify_position_margin**  
  Modify isolated position margin.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `amount`: Amount to modify  
  - `position_side`: `'BOTH'`, `'LONG'`, or `'SHORT'`  
  - `margin_type`: `1` for add, `2` for reduce

- **get_position_margin_history**  
  Get position margin modification history.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `margin_type`: `1` for add, `2` for reduce  
  - `limit`: Number of entries

- **change_leverage**  
  Change initial leverage for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `leverage`: Target leverage (1-125)

- **change_margin_type**  
  Change margin type between isolated and cross.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `margin_type`: `'ISOLATED'` or `'CROSSED'`

- **get_leverage_brackets**  
  Get notional and leverage brackets for a symbol.

- **get_adl_quantile**  
  Get position ADL quantile estimation for a symbol.

- **get_commission_rate**  
  Get user's commission rate for a symbol.

### Order Management

- **place_order**  
  Place a futures order of any type (MARKET, LIMIT, STOP, STOP_MARKET, TRAILING_STOP_MARKET, etc).  
  Args:  
  - `symbol`, `side`, `type`, and other order parameters

- **place_multiple_orders**  
  Place multiple orders at once.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `orders`: List of order parameters (see code for details)

- **query_order**  
  Query a specific order's status.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `order_id`: Order ID

- **cancel_order**  
  Cancel an active order.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `order_id`: Order ID

- **cancel_all_orders**  
  Cancel all open orders for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol

- **cancel_multiple_orders**  
  Cancel multiple orders.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `order_id_list`: List of order IDs

- **auto_cancel_all_orders**  
  Set up auto-cancellation of all orders after a countdown.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `countdown_time`: Countdown in milliseconds

- **get_open_order**  
  Query current open order by order id.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `order_id`: Order ID

- **get_open_orders**  
  Get all open futures orders for a specific symbol.  
  Args:  
  - `symbol`: Trading pair symbol

- **get_all_orders**  
  Get all account orders.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `order_id`, `start_time`, `end_time`, `limit` (optional)

- **get_account_trades**  
  Get account trade list.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `start_time`, `end_time`, `from_id`, `limit` (optional)

- **get_income_history**  
  Get income history.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `income_type`, `start_time`, `end_time`, `limit` (optional)

- **get_force_orders**  
  Get user's force orders.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `auto_close_type`, `start_time`, `end_time`, `limit` (optional)

### Market Data

- **get_order_book**  
  Get order book for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `limit`: Number of bids/asks (5,10,20,50,100,500,1000)

- **get_aggregate_trades**  
  Get compressed, aggregate market trades.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `from_id`, `start_time`, `end_time`, `limit` (optional)

- **get_klines**  
  Get kline/candlestick data for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `interval`: Kline interval  
  - `start_time`, `end_time`, `limit` (optional)

- **get_mark_price**  
  Get mark price and funding rate for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol

- **get_funding_rate_history**  
  Get funding rate history for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol  
  - `start_time`, `end_time`, `limit` (optional)

- **get_price_ticker**  
  Get latest price for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol

- **get_book_ticker**  
  Get best price/qty on the order book for a symbol.  
  Args:  
  - `symbol`: Trading pair symbol

---

## Project Structure

```
.
├── src/
│   └── trade_mcp/
│       ├── api/         # Trading and market data logic
│       └── server/      # MCP server and tool setup
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── README.md
```

---

## Development & Advanced

- To run directly: `python -m trade_mcp.server.main --api-key ...`
- To build a package: `uv pip install .`
- Docker support: see `Dockerfile`, `image_build.sh`, and `image_deploy.sh`.

---

## License

MIT 