# ERP Sales Order Data Cleaner (GUI)

An automated desktop tool built with Python, Pandas, and PyWebView to clean, parse, and transform messy raw sales invoice CSV/Excel exports into structured, ERPNext/Frappe-ready Sales Order import formats.

---

## 🚀 Key Features

* **Desktop Web UI:** Clean and intuitive modern interface powered by `pywebview`.
* **Automatic ERP Mapping:** Maps local item names and descriptions directly to ERP Codes using `ERP Code - Sheet1.csv`.
* **Dynamic Source Warehouse Calculation:** Automatically structures warehouses based on currency/payment type (`USD`/`MMK`), invoice location (`PT`, `Z5`, `SB`, etc.), and special handling for Interest items (`{Location} (Interest) MMK - SYS`).
* **Flexible ID Numbering:** Preserves custom prefix formats and digit padding (e.g., `SAL-ORD-2026-00356`).
* **Discount & Price Precision:** Captures individual line item rates and header-level voucher discounts accurately.
* **Auto-organized Exports:** Cleaned files are saved automatically into the `cleaned_csv/` directory.

---

## 📂 Project Structure

```text
├── app_webview.py            # Main application script
├── ERP Code - Sheet1.csv     # Master ERP Item Code mapping database
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignored patterns
├── README.md                 # Project documentation
└── cleaned_csv/              # Auto-created output directory for cleaned files
```
🪟 Windows Setup
1. Prerequisites
Download and install Python 3.10+ from python.org.

⚠️ Important: During installation, make sure to check the box "Add python.exe to PATH".

2. Environment Setup & Run (Command Prompt / PowerShell)
```
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch Application
python app_webview.py
```
🍏 macOS Setup
1. Prerequisites
Make sure Python 3 is installed. If using Homebrew:
```
brew install python
```
2. Environment Setup & Run (Terminal)
```
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (Install pyobjc for macOS native WebKit integration)
pip install -r requirements.txt
pip install pyobjc-framework-WebKit

# Launch Application
python app_webview.py
```
🐧 Linux (Ubuntu / Debian / Mint) Setup
1. System Dependencies
Linux requires Qt/WebKit or GTK backend packages to render WebViews:
```
sudo apt update
sudo apt install python3-pip python3-venv -y
```
2. Environment Setup & Run (Terminal)
```
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install core dependencies along with Qt bindings
pip install -r requirements.txt
pip install PyQt6 PyQt6-WebEngine qtpy

# Launch Application
python app_webview.py
```
📖 How to Use
Launch the application via python app_webview.py.

Click Browse under Raw CSV File and select your uncleaned sales report.

Ensure the ERP Mapping File (ERP Code - Sheet1.csv) is present in the workspace.

Customize your ERP configuration if needed:

Starting ID: Enter starting ID (e.g., SAL-ORD-2026-00356).

Company Name, Series, Currency, Delivery Date, etc.

Click ⚡ Start Data Cleaning.

The cleaned file will be generated and saved inside the cleaned_csv/ folder.

Upload the output file directly to ERPNext > Sales Order > Import Data.

📦 Requirements
pywebview

pandas

pythonnet (for Windows platform support)

PyQt6 / PyQt6-WebEngine / qtpy (for Linux platform support)

pyobjc-framework-WebKit (for macOS platform support)
