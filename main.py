from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import yfinance as yf
import matplotlib.pyplot as plt

class StockChart(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        symbol = "VOO"  # S&P 500 ETF
        data = yf.download(symbol, period="6mo")
        fig, ax = plt.subplots()
        data['Close'].plot(ax=ax, title=f"{symbol} Close Price")
        self.add_widget(FigureCanvasKivyAgg(fig))

class StockApp(App):
    def build(self):
        return StockChart()

if __name__ == "__main__":
    StockApp().run()
