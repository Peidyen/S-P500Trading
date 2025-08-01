from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.widget import Widget

import matplotlib
matplotlib.use('Agg')  # Safe backend for Android & embedded use

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# Set window size (optional for Android debugging)
Window.size = (1000, 800)

# Disable touch interaction with matplotlib canvas
class NoTouchCanvas(FigureCanvasKivyAgg):
    def on_touch_down(self, touch): return False
    def on_touch_move(self, touch): return False
    def on_touch_up(self, touch): return False

    # Stub this to prevent crash
    def motion_notify_event(self, x, y, guiEvent=None):
        pass


# Get live S&P 500 symbols from Wikipedia
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    df = pd.read_html(url, header=0)[0]
    return df['Symbol'].tolist()

# Main scrollable chart layout
class StockScroll(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        grid.bind(minimum_height=grid.setter('height'))

        tickers = get_sp500_tickers()[:10]  # Limit to 10 for performance
        for symbol in tickers:
            try:
                data = yf.download(symbol, period="1mo", progress=False)
                if data.empty:
                    continue

                fig, ax = plt.subplots(figsize=(8, 3))
                data['Close'].plot(ax=ax, title=symbol)
                ax.set_ylabel("Price ($)")
                fig.tight_layout()

                canvas = NoTouchCanvas(fig)
                canvas.size_hint_y = None
                canvas.height = 300

                grid.add_widget(canvas)

            except Exception as e:
                print(f"Error loading {symbol}: {e}")

        scroll.add_widget(grid)
        self.add_widget(scroll)

# App entry point
class SP500App(App):
    def build(self):
        return StockScroll()

if __name__ == '__main__':
    SP500App().run()
