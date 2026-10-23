import argparse
import numpy as np
import pandas as pd
import yfinance as yf

class DiscretionaryVolCatalystDesk:
    """
    Live Discretionary Volatility Desk: Fetches market FX data, estimates rolling volatility,
    and applies a discretionary macro catalyst decision framework.
    """
    def __init__(self, ticker: str = "ZAR=X"):
        self.ticker = ticker

    def fetch_market_volatility(self, window: int = 21) -> float:
        """Fetches live FX price data and calculates 21-day annualized historical volatility."""
        data = yf.download(self.ticker, period="3m", progress=False)
        if data.empty:
            raise ValueError(f"Unable to fetch data for ticker {self.ticker}")
        
        close_prices = data['Close'].squeeze()
        log_returns = np.log(close_prices / close_prices.shift(1)).dropna()
        annualized_vol = log_returns.tail(window).std() * np.sqrt(252)
        return float(annualized_vol)

    def evaluate(self, quant_predicted_iv: float, event_name: str, high_impact: bool, macro_regime: str) -> dict:
        market_vol = self.fetch_market_volatility()
        vol_mispricing_bps = (quant_predicted_iv - market_vol) * 10000
        
        recommendation = "NO TRADE"
        conviction = "LOW"

        if high_impact:
            if vol_mispricing_bps > 100 and macro_regime.upper() in ["POLICY_DIVERGENCE", "HAWKISH_PIVOT"]:
                recommendation = "LONG VOLATILITY (Buy Straddle / Calendar Spread)"
                conviction = "HIGH"
            elif vol_mispricing_bps < -100 and macro_regime.upper() in ["LIQUIDITY_EXPANSION", "DOVISH_PAUSE"]:
                recommendation = "SHORT VOLATILITY (Sell Premium / Iron Condor)"
                conviction = "MEDIUM"
            else:
                recommendation = "TACTICAL PASS (Wait for Event Clear)"
                conviction = "NEUTRAL"

        return {
            "Ticker": self.ticker,
            "Event": event_name,
            "Market_Annualized_Vol": f"{market_vol:.2%}",
            "Quant_Model_IV": f"{quant_predicted_iv:.2%}",
            "Mispricing_bps": round(vol_mispricing_bps, 2),
            "Macro_Regime": macro_regime,
            "Discretionary_Action": recommendation,
            "Conviction": conviction
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discretionary Volatility Catalyst Desk")
    parser.add_argument("--ticker", type=str, default="ZAR=X", help="FX Ticker (e.g. ZAR=X, EURUSD=X)")
    parser.add_argument("--quant_iv", type=float, default=0.185, help="Quant Model Predicted IV (e.g. 0.185 for 18.5%)")
    parser.add_argument("--event", type=str, default="SARB Interest Rate Decision", help="Catalyst Event Name")
    parser.add_argument("--regime", type=str, default="POLICY_DIVERGENCE", help="Macro Regime Context")
    args = parser.parse_args()

    desk = DiscretionaryVolCatalystDesk(ticker=args.ticker)
    result = desk.evaluate(quant_predicted_iv=args.quant_iv, event_name=args.event, high_impact=True, macro_regime=args.regime)
    
    print("\n================ DISCRETIONARY VOLATILITY DESK ================")
    for k, v in result.items():
        print(f"{k:<25}: {v}")
    print("================================================================\n")
