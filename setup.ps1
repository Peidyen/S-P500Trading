# PowerShell Script to Set Up Kivy Stock App

$envName = "venv"

Write-Host "🔧 Creating virtual environment..."
python -m venv $envName

$activate = ".\$envName\Scripts\Activate.ps1"
if (-Not (Test-Path $activate)) {
    Write-Host "❌ Could not find activate script. Exiting."
    exit 1
}

Write-Host "✅ Virtual environment created. Activating..."
& $activate

Write-Host "📦 Installing required packages..."
pip install --upgrade pip
pip install kivy kivy-garden matplotlib yfinance pandas requests

Write-Host "🌱 Installing Kivy Garden matplotlib widget..."
python -m garden install matplotlib

# Write basic main.py
$mainCode = @'
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
'@
Set-Content -Path "main.py" -Value $mainCode
Write-Host "✅ Wrote main.py"

# Write .gitignore
$gitignore = @'
__pycache__/
*.py[cod]
*.pyo
*.so
*.log
*.pdf
*.png
.buildozer/
bin/
build/
dist/
*.apk
*.aab
venv/
.idea/
.vscode/
.kivy/
.kivy-garden/
'@
Set-Content -Path ".gitignore" -Value $gitignore
Write-Host "✅ Wrote .gitignore"

# Run the app
Write-Host "🚀 Launching app..."
python main.py
