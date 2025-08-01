from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Set default window size
Window.size = (1000, 800)

# Get live list of S&P 500 tickers from Wikipedia
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    df = pd.read_html(url, header=0)[0]
    return df['Symbol'].tolist()

# Main layout that scrolls through multiple stock charts
class StockScroll(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # ScrollView holds all charts
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        grid.bind(minimum_height=grid.setter('height'))

        tickers = get_sp500_tickers()[:10]  # ⚠️ Adjust this number to load more

        for symbol in tickers:
            try:
                data = yf.download(symbol, period="1mo", progress=False)
                if data.empty:
                    continue

                fig, ax = plt.subplots(figsize=(8, 3))
                data['Close'].plot(ax=ax, title=symbol)
                ax.set_ylabel("Price ($)")
                fig.tight_layout()

                canvas = FigureCanvasKivyAgg(fig)
                canvas.size_hint_y = None
                canvas.height = 300

                grid.add_widget(canvas)

            except Exception as e:
                print(f"Error loading {symbol}: {e}")

        scroll.add_widget(grid)
        self.add_widget(scroll)

# Kivy App
class SP500App(App):
    def build(self):
        return StockScroll()

if __name__ == '__main__':
    SP500App().run()
