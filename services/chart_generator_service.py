import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from datetime import datetime
from scipy.stats import linregress
from config.logger import setup_logging

logger = setup_logging()

class ChartGeneratorService:
    def __init__(self, output_dir="charts"):
        self.output_dir = output_dir

    def generate_single_chart(self, symbol, df, candlestick_interval, projection_points=5):
        current_date = datetime.now().strftime("%Y-%m-%d")
        dated_folder = os.path.join(self.output_dir, current_date)
        os.makedirs(dated_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%H-%M-%S")
        output_file = os.path.join(dated_folder, f"{symbol}-{timestamp}.png")

        try:
            if "open_time" not in df.columns:
                logger.error(f"Missing 'open_time' column in data for {symbol}.")
                return None

            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms').map(mdates.date2num)

            time_range = df['open_time'].max() - df['open_time'].min()
            candlestick_width = max(0.0005, time_range / len(df) / 2)

            fig = plt.figure(figsize=(12, 8), facecolor="black")
            ax_candles, ax_volume = fig.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [4, 1]})
            ax_candles.set_facecolor("black")
            ax_volume.set_facecolor("black")

            symbol_title = symbol.replace("USD", " / USD") if "USD" in symbol else symbol

            ohlc = df[["open_time", "open", "high", "low", "close"]].values
            candlestick_ohlc(ax_candles, ohlc, width=candlestick_width, colorup='lime', colordown='red', alpha=0.9)
            ax_candles.set_title(f"{symbol_title} - Last {len(df)} Candlesticks ({candlestick_interval} Interval)", color="white", fontsize=14)
            ax_candles.set_ylabel("Price", color="white")
            ax_candles.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)
            ax_candles.tick_params(axis='both', colors="white")

            avg_price = (df['high'] + df['low']) / 2
            x_values = df['open_time']
            slope, intercept, _, _, _ = linregress(x_values, avg_price)
            trendline = slope * x_values + intercept
            ax_candles.plot(df['open_time'], trendline, color='magenta', linestyle='--', linewidth=1, label='Trend Line')

            last_time = df['open_time'].iloc[-1]
            time_step = x_values.iloc[1] - x_values.iloc[0]
            future_times = [last_time + i * time_step for i in range(1, projection_points + 1)]
            future_trendline = [slope * t + intercept for t in future_times]
            ax_candles.plot(future_times, future_trendline, color='orange', linestyle='dotted', linewidth=1, label='Future Trend Line')

            current_price = df['close'].iloc[-1]
            ax_candles.axhline(current_price, color='cyan', linestyle='--', linewidth=1, label=f'Current Price: {current_price:.2f}')

            ax_candles.xaxis_date()
            ax_candles.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax_candles.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            ax_candles.tick_params(axis='x', colors="white")

            handles, labels = ax_candles.get_legend_handles_labels()
            if labels:
                ax_candles.legend(loc='upper left', fontsize=8, facecolor="black", edgecolor="white", labelcolor="white")

            if "volume" in df:
                volume_colors = ['lime' if df['close'].iloc[i] >= df['open'].iloc[i] else 'red' for i in range(len(df))]
                ax_volume.bar(df['open_time'], df['volume'], color=volume_colors, alpha=0.7, width=candlestick_width)
                ax_volume.set_ylabel("Volume", color="white")
                ax_volume.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)
                ax_volume.tick_params(axis='both', colors="white")
                ax_volume.set_ylim(0, df['volume'].max() * 1.1)

            ax_volume.get_yaxis().get_major_formatter().set_scientific(False)
            plt.subplots_adjust(hspace=0.05)
            plt.tight_layout(pad=2)
            plt.savefig(output_file, facecolor="black")
            plt.close()

            logger.info(f"Chart saved for {symbol}: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error generating chart for {symbol}: {e}")
            return None