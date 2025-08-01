from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import yfinance as yf
import matplotlib.pyplot as plt
from kivy.uix.label import Label
from kivy.core.window import Window

Window.size = (800, 600)

class StockChart(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        symbol = "VOO"  # S&P 500 ETF

        try:
            data = yf.download(symbol, period="6mo")
            if data is None or data.empty:
                raise ValueError("No data downloaded.")

            fig, ax = plt.subplots()
            data['Close'].plot(ax=ax, title=f"{symbol} Close Price")
            self.add_widget(FigureCanvasKivyAgg(fig))

        except Exception as e:
            self.add_widget(Label(text=f"Failed to load data: {e}"))

class StockApp(App):
    def build(self):
        return StockChart()

if __name__ == "__main__":
    StockApp().run()
