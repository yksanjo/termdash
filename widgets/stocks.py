"""Stock and cryptocurrency widgets."""

import os
import json
import urllib.request
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import deque

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from ..widget import Widget, WidgetConfig


class StockWidget(Widget):
    """Widget displaying stock prices."""
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 symbols: Optional[List[str]] = None,
                 api_key: Optional[str] = None):
        if config is None:
            config = WidgetConfig(
                name="stocks",
                title="📈 Stocks",
                refresh_interval=60.0,
                border_style="green"
            )
        super().__init__(config)
        self.symbols = symbols or ["AAPL", "GOOGL", "MSFT"]
        self.api_key = api_key or os.environ.get("ALPHA_VANTAGE_API_KEY")
        self._fallback_mode = self.api_key is None
        self.price_history: Dict[str, deque] = {sym: deque(maxlen=20) for sym in self.symbols}
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch stock data."""
        if self._fallback_mode:
            return self._get_fallback_data()
        
        results = []
        for symbol in self.symbols[:3]:  # Limit to 3 for free API
            try:
                url = (
                    f"https://www.alphavantage.co/query?"
                    f"function=GLOBAL_QUOTE&"
                    f"symbol={symbol}&"
                    f"apikey={self.api_key}"
                )
                
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                
                quote = data.get("Global Quote", {})
                if quote:
                    price = float(quote.get("05. price", 0))
                    change = float(quote.get("09. change", 0))
                    change_pct = quote.get("10. change percent", "0%").replace("%", "")
                    
                    self.price_history[symbol].append(price)
                    
                    results.append({
                        "symbol": symbol,
                        "price": price,
                        "change": change,
                        "change_pct": float(change_pct),
                        "volume": int(quote.get("06. volume", 0)),
                        "success": True
                    })
                    
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    def _get_fallback_data(self) -> List[Dict[str, Any]]:
        """Generate demo stock data."""
        import random
        
        base_prices = {
            "AAPL": 175.0,
            "GOOGL": 140.0,
            "MSFT": 380.0,
            "AMZN": 180.0,
            "TSLA": 200.0,
            "NVDA": 850.0
        }
        
        results = []
        for symbol in self.symbols:
            base = base_prices.get(symbol, 100.0)
            # Random walk
            prev_price = list(self.price_history[symbol])[-1] if self.price_history[symbol] else base
            change = random.uniform(-base * 0.02, base * 0.02)
            price = prev_price + change
            change_pct = (change / prev_price) * 100 if prev_price else 0
            
            self.price_history[symbol].append(price)
            
            results.append({
                "symbol": symbol,
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "volume": random.randint(1000000, 50000000),
                "success": False,
                "demo": True
            })
        
        return results
    
    def render(self) -> Panel:
        """Render stock prices."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        table = Table(expand=True, box=None)
        table.add_column("Symbol", style="bold cyan")
        table.add_column("Price", style="green", justify="right")
        table.add_column("Change", justify="right")
        table.add_column("Chart")
        
        for stock in self.data:
            if not stock.get("success") and not stock.get("demo"):
                table.add_row(stock["symbol"], "Error", "", "")
                continue
            
            symbol = stock["symbol"]
            price = stock["price"]
            change = stock["change"]
            change_pct = stock["change_pct"]
            
            # Color based on change
            change_style = "green" if change >= 0 else "red"
            change_symbol = "▲" if change >= 0 else "▼"
            
            change_text = Text(
                f"{change_symbol} ${abs(change):.2f} ({abs(change_pct):.2f}%)",
                style=change_style
            )
            
            # Mini sparkline
            history = list(self.price_history.get(symbol, []))[-10:]
            spark = self._sparkline(history)
            
            table.add_row(
                symbol,
                f"${price:.2f}",
                change_text,
                Text(spark, style=change_style)
            )
        
        footer = None
        if any(s.get("demo") for s in self.data):
            footer = Text("Demo mode - Add ALPHA_VANTAGE_API_KEY", style="dim yellow")
        elif self.config.show_footer:
            footer = self.get_footer_text()
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            subtitle=footer
        )
    
    def _sparkline(self, data: List[float]) -> str:
        """Create ASCII sparkline."""
        if len(data) < 2:
            return ""
        
        blocks = "▁▂▃▄▅▆▇█"
        min_val, max_val = min(data), max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        result = ""
        for val in data:
            idx = int(((val - min_val) / range_val) * (len(blocks) - 1))
            idx = min(idx, len(blocks) - 1)
            result += blocks[idx]
        return result


class CryptoWidget(Widget):
    """Widget displaying cryptocurrency prices."""
    
    COINS = {
        "bitcoin": "BTC",
        "ethereum": "ETH",
        "solana": "SOL",
        "cardano": "ADA",
        "polkadot": "DOT"
    }
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 coins: Optional[List[str]] = None):
        if config is None:
            config = WidgetConfig(
                name="crypto",
                title="₿ Crypto",
                refresh_interval=30.0,
                border_style="bright_yellow"
            )
        super().__init__(config)
        self.coins = coins or ["bitcoin", "ethereum"]
        self.price_history: Dict[str, deque] = {c: deque(maxlen=20) for c in self.coins}
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency data from CoinGecko API (free, no key needed)."""
        try:
            ids = ",".join(self.coins)
            url = (
                f"https://api.coingecko.com/api/v3/simple/price?"
                f"ids={ids}&"
                f"vs_currencies=usd&"
                f"include_24hr_change=true&"
                f"include_24hr_vol=true&"
                f"include_market_cap=true"
            )
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            results = []
            for coin_id in self.coins:
                if coin_id in data:
                    coin_data = data[coin_id]
                    price = coin_data.get("usd", 0)
                    change_24h = coin_data.get("usd_24h_change", 0)
                    volume = coin_data.get("usd_24h_vol", 0)
                    market_cap = coin_data.get("usd_market_cap", 0)
                    
                    self.price_history[coin_id].append(price)
                    
                    results.append({
                        "id": coin_id,
                        "symbol": self.COINS.get(coin_id, coin_id.upper()),
                        "price": price,
                        "change_24h": change_24h,
                        "volume": volume,
                        "market_cap": market_cap,
                        "success": True
                    })
            
            return results
            
        except Exception as e:
            # Return demo data on error
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> List[Dict[str, Any]]:
        """Generate demo crypto data."""
        import random
        
        base_prices = {
            "bitcoin": 65000.0,
            "ethereum": 3500.0,
            "solana": 140.0,
            "cardano": 0.5,
            "polkadot": 7.0
        }
        
        results = []
        for coin_id in self.coins:
            base = base_prices.get(coin_id, 1.0)
            prev_price = list(self.price_history[coin_id])[-1] if self.price_history[coin_id] else base
            change = random.uniform(-0.05, 0.05)
            price = prev_price * (1 + change)
            
            self.price_history[coin_id].append(price)
            
            results.append({
                "id": coin_id,
                "symbol": self.COINS.get(coin_id, coin_id.upper()),
                "price": price,
                "change_24h": change * 100,
                "volume": random.uniform(1000000000, 10000000000),
                "market_cap": price * random.uniform(18000000, 21000000),
                "success": False,
                "demo": True
            })
        
        return results
    
    def render(self) -> Panel:
        """Render crypto prices."""
        if not self.data:
            return Panel("Loading...", title=self.config.title,
                        border_style=self.config.border_style)
        
        table = Table(expand=True, box=None)
        table.add_column("Coin", style="bold yellow")
        table.add_column("Price", style="green", justify="right")
        table.add_column("24h %", justify="right")
        table.add_column("Trend")
        
        for coin in self.data:
            symbol = coin["symbol"]
            price = coin["price"]
            change = coin["change_24h"]
            
            # Format price
            if price >= 1000:
                price_str = f"${price:,.2f}"
            elif price >= 1:
                price_str = f"${price:.2f}"
            else:
                price_str = f"${price:.4f}"
            
            # Color based on change
            change_style = "green" if change >= 0 else "red"
            change_symbol = "▲" if change >= 0 else "▼"
            
            change_text = Text(
                f"{change_symbol} {abs(change):.2f}%",
                style=change_style
            )
            
            # Mini sparkline
            history = list(self.price_history.get(coin["id"], []))[-10:]
            spark = self._sparkline(history)
            
            table.add_row(
                f"{symbol}",
                price_str,
                change_text,
                Text(spark, style=change_style)
            )
        
        footer = None
        if any(c.get("demo") for c in self.data):
            footer = Text("Demo mode", style="dim yellow")
        elif self.config.show_footer:
            footer = self.get_footer_text()
        
        return Panel(
            table,
            title=self.config.title if self.config.show_header else None,
            border_style=self.config.border_style,
            subtitle=footer
        )
    
    def _sparkline(self, data: List[float]) -> str:
        """Create ASCII sparkline."""
        if len(data) < 2:
            return ""
        
        blocks = "▁▂▃▄▅▆▇█"
        min_val, max_val = min(data), max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        result = ""
        for val in data:
            idx = int(((val - min_val) / range_val) * (len(blocks) - 1))
            idx = min(idx, len(blocks) - 1)
            result += blocks[idx]
        return result
