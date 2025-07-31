from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.clipboard import Clipboard
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import webbrowser

# === Technical Indicator Functions ===
def compute_rsi(close, window=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_macd(close, short=12, long=26, signal=9):
    ema_short = close.ewm(span=short, adjust=False).mean()
    ema_long = close.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

# === Fetch S&P 500 Symbols ===
def get_sp500_symbols():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(requests.get(url).text)
    symbols = tables[0]['Symbol'].tolist()
    return sorted(set(symbols))

# === Kivy Widget ===
class StockWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.label = Label(text="📈 S&P 500 Signal Viewer", font_size=24, size_hint=(1, 0.1))
        self.add_widget(self.label)

        self.symbols = get_sp500_symbols()
        self.selected_symbol = self.symbols[0]

        self.dropdown = DropDown()
        for sym in self.symbols:
            btn = Button(text=sym, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_symbol(btn.text))
            self.dropdown.add_widget(btn)

        self.main_button = Button(text=self.selected_symbol, size_hint=(1, 0.1))
        self.main_button.bind(on_release=self.dropdown.open)
        self.add_widget(self.main_button)

        self.signal_label = Label(text="", size_hint=(1, 0.2))
        self.add_widget(self.signal_label)

        self.plot_button = Button(text="📊 View Chart", size_hint=(1, 0.1))
        self.plot_button.bind(on_release=self.show_chart)
        self.add_widget(self.plot_button)

        self.pdf_button = Button(text="📄 Open PDF", size_hint=(1, 0.1))
        self.pdf_button.bind(on_release=self.open_pdf)
        self.add_widget(self.pdf_button)

    def select_symbol(self, symbol):
        self.selected_symbol = symbol
        self.main_button.text = symbol
        self.dropdown.dismiss()

    def show_chart(self, instance):
        symbol = self.selected_symbol
        df = yf.download(symbol, period="6mo")
        close = df['Close']
        rsi = compute_rsi(close)
        macd, signal_line = compute_macd(close)

        # Signal Summary
        rsi_val = rsi.iloc[-1]
        macd_val = macd.iloc[-1]
        signal_val = signal_line.iloc[-1]
        rsi_status = "Oversold" if rsi_val < 30 else "Overbought" if rsi_val > 70 else "Neutral"
        macd_status = "Bullish Crossover" if macd_val > signal_val and macd.iloc[-2] <= signal_line.iloc[-2] else \
                      "Bearish Crossover" if macd_val < signal_val and macd.iloc[-2] >= signal_line.iloc[-2] else "Neutral"
        self.signal_label.text = f"RSI: {rsi_status}\nMACD: {macd_status}"

        # Plotting
        fig, axs = plt.subplots(3, 1, figsize=(6, 6), sharex=True, tight_layout=True)
        axs[0].plot(df.index, close, label="Close Price", color='black')
        axs[0].set_ylabel("Price")
        axs[0].legend()

        axs[1].plot(rsi.index, rsi, label="RSI", color='blue')
        axs[1].axhline(70, color='red', linestyle='--')
        axs[1].axhline(30, color='green', linestyle='--')
        axs[1].set_ylabel("RSI")
        axs[1].legend()

        axs[2].plot(macd.index, macd, label="MACD", color='purple')
        axs[2].plot(signal_line.index, signal_line, label="Signal Line", color='orange')
        axs[2].axhline(0, color='gray', linestyle='--')
        axs[2].set_ylabel("MACD")
        axs[2].legend()

        if hasattr(self, 'plot'):
            self.remove_widget(self.plot)
        self.plot = FigureCanvasKivyAgg(fig)
        self.add_widget(self.plot)

        # Save PDF
        with PdfPages("signal_chart.pdf") as pdf_out:
            pdf_out.savefig(fig)

        Clipboard.copy("signal_chart.pdf")

    def open_pdf(self, instance):
        pdf_path = os.path.abspath("signal_chart.pdf")
        try:
            webbrowser.open(f"file://{pdf_path}")
        except Exception as e:
            print("❌ Unable to open PDF:", e)

# === Kivy App ===
class StockApp(App):
    def build(self):
        return StockWidget()

if __name__ == '__main__':
    StockApp().run()
