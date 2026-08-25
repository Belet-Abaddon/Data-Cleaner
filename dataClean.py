import os
import csv
import re
import webview
from webview import FileDialog
import pandas as pd

# ERPNext Sales Invoice Standard 360 Columns List
SALES_INVOICE_COLUMNS = [
    'Company', 'Series', 'Customer', 'Posting Date', 'Currency', 'Exchange Rate', 
    'Price List', 'Price List Currency', 'Price List Exchange Rate', 'Net Total (Company Currency)', 
    'Grand Total', 'base_grand_total', 'Debit To', 'Company Tax ID', 'Customer Name', 'Tax Id', 
    'Posting Time', 'Edit Posting Date and Time', 'Payment Due Date', 'Include Payment (POS)', 
    'POS Profile', 'Is Consolidated', 'Is Return (Credit Note)', 'Return Against', 
    'Update Outstanding for Self', 'Update Billed Amount in Sales Order', 
    'Update Billed Amount in Delivery Note', 'Is Rate Adjustment Entry (Debit Note)', 
    'Consider for Tax Withholding', 'Amended From', 'Is created using POS', 'POS Closing Entry', 
    'Has Subcontracted', 'Cost Center', 'Project', 'Ignore Pricing Rule', 'Scan Barcode', 
    'Update Stock', 'Source Warehouse', 'Set Target Warehouse', 'Total Quantity', 
    'Total Net Weight', 'Total (Company Currency)', 'Total', 'Net Total', 'Tax Category', 
    'Sales Taxes and Charges Template', 'Shipping Rule', 'Incoterm', 'Named Place', 
    'Total Taxes and Charges (Company Currency)', 'Total Taxes and Charges', 
    'Use Company default Cost Center for Round off', 'In Words', 'Disable Rounded Total', 
    'Rounding Adjustment', 'Rounded Total', 'base_in_words', 'base_rounding_adjustment', 
    'base_rounded_total', 'Total Advance', 'Outstanding Amount', 'Tax Withholding Group', 
    'Ignore Tax Withholding Threshold', 'Edit Tax Withholding Entries', 'Apply Additional Discount On', 
    'Additional Discount Amount (Company Currency)', 'Coupon Code', 'Additional Discount Percentage', 
    'Additional Discount Amount', 'Is Cash or Non Trade Discount', 'Discount Account', 
    'Taxes and Charges Calculation', 'Total Billing Hours', 'Total Billing Amount', 
    'Cash/Bank Account', 'Paid Amount (Company Currency)', 'Paid Amount', 
    'Base Change Amount (Company Currency)', 'Change Amount', 'Account for Change Amount', 
    'Allocate Advances Automatically (FIFO)', 'Only Include Allocated Payments', 
    'Write Off Amount', 'Write Off Amount (Company Currency)', 'Write Off Outstanding Amount', 
    'Write Off Account', 'Write Off Cost Center', 'Redeem Loyalty Points', 'Loyalty Points', 
    'Loyalty Amount', 'Loyalty Program', "Don't Create Loyalty Points", 'Redemption Account', 
    'Redemption Cost Center', 'Customer Address', 'Address', 'Contact Person', 'Contact', 
    'Mobile No', 'Contact Email', 'Territory', 'Shipping Address Name', 'Shipping Address', 
    'Dispatch Address Name', 'Dispatch Address', 'Company Address Name', 'Company Address', 
    'Company Contact Person', 'Ignore Default Payment Terms Template', 'Payment Terms Template', 
    'Terms', 'Terms and Conditions Details', "Customer's Purchase Order", "Customer's Purchase Order Date", 
    'Party Account Currency', 'Is Opening Entry', 'Unrealized Profit / Loss Account', 
    'Against Income Account', 'Sales Partner', 'Amount Eligible for Commission', 
    'Commission Rate (%)', 'Total Commission', 'Letter Head', 'Group same items', 
    'Print Heading', 'Print Language', 'Subscription', 'From Date', 'To Date', 'Auto Repeat', 
    'Source', 'Medium', 'Campaign', 'Content', 'Status', 'Remarks', 'Customer Group', 'Title', 
    'Is Internal Customer', 'Represents Company', 'Inter Company Invoice Reference', 'Is Discounted', 
    'Amount (Items)', 'Amount (Company Currency) (Items)', 'Cost Center (Items)', 
    'Income Account (Items)', 'Item Name (Items)', 'Rate (Items)', 
    'Rate (Company Currency) (Items)', 'UOM (Items)', 'UOM Conversion Factor (Items)', 
    'Against Pick List (Items)', 'Allow Zero Valuation Rate (Items)', 'Asset (Items)', 
    'Available Batch Qty at Warehouse (Items)', 'Barcode (Items)', 'Batch No (Items)', 
    'Brand Name (Items)', 'Consider for Tax Withholding (Items)', "Customer's Item Code (Items)", 
    'Deferred Revenue Account (Items)', 'Delivered By Supplier (Items)', 'Delivered Qty (Items)', 
    'Delivery Note (Items)', 'Delivery Note Item (Items)', 'Description (Items)', 
    'Discount (%) on Price List Rate with Margin (Items)', 'Discount Account (Items)', 
    'Discount Amount (Items)', 'Distributed Discount Amount (Items)', 
    'Enable Deferred Revenue (Items)', 'Expense Account (Items)', 'Finance Book (Items)', 
    'Grant Commission (Items)', 'Has Item Scanned (Items)', 'Image (Items)', 
    'Incoming Rate (Costing) (Items)', 'Is Fixed Asset (Items)', 'Is Free Item (Items)', 
    'Is Product Bundle (Items)', 'Item (Items)', 'Item Group (Items)', 'Item Tax Rate (Items)', 
    'Item Tax Template (Items)', 'Margin Rate or Amount (Items)', 'Margin Type (Items)', 
    'Net Amount (Items)', 'Net Amount (Company Currency) (Items)', 'Net Rate (Items)', 
    'Net Rate (Company Currency) (Items)', 'Page Break (Items)', 'Pick List Item (Items)', 
    'POS Invoice (Items)', 'POS Invoice Item (Items)', 'Price List Rate (Items)', 
    'Price List Rate (Company Currency) (Items)', 'Pricing Rules (Items)', 
    'Product Bundle (Items)', 'Project (Items)', 'Purchase Order (Items)', 
    'Purchase Order Item (Items)', 'Qty (Company) (Items)', 'Qty (Warehouse) (Items)', 
    'Qty as per Stock UOM (Items)', 'Quality Inspection (Items)', 'Quantity (Items)', 
    'Rate of Stock UOM (Items)', 'Rate With Margin (Items)', 
    'Rate With Margin (Company Currency) (Items)', 'Sales Invoice Item (Items)', 
    'Sales Order (Items)', 'Sales Order Item (Items)', 'SCIO Detail (Items)', 
    'Serial and Batch Bundle (Items)', 'Serial No (Items)', 'Service End Date (Items)', 
    'Service Start Date (Items)', 'Service Stop Date (Items)', 'Stock UOM (Items)', 
    'Target Warehouse (Items)', 'Tax Withholding Category (Items)', 'Total Weight (Items)', 
    'Use Serial No / Batch Fields (Items)', 'Warehouse (Items)', 'Weight Per Unit (Items)', 
    'Weight UOM (Items)', 'Account Currency (Sales Taxes and Charges)', 
    'Account Head (Sales Taxes and Charges)', 'Amount (Sales Taxes and Charges)', 
    'Amount (Company Currency) (Sales Taxes and Charges)', 
    'Considered In Paid Amount (Sales Taxes and Charges)', 
    'Cost Center (Sales Taxes and Charges)', 'Description (Sales Taxes and Charges)', 
    "Don't Recompute Tax (Sales Taxes and Charges)", 
    'Is Tax Withholding Account (Sales Taxes and Charges)', 
    'Is this Tax included in Basic Rate? (Sales Taxes and Charges)', 
    'Net Amount (Sales Taxes and Charges)', 
    'Net Amount (Company Currency) (Sales Taxes and Charges)', 
    'Project (Sales Taxes and Charges)', 'Reference Row # (Sales Taxes and Charges)', 
    'Set by Item Tax Template (Sales Taxes and Charges)', 
    'Tax Amount After Discount Amount (Sales Taxes and Charges)', 
    'Tax Amount After Discount Amount (Company Currency) (Sales Taxes and Charges)', 
    'Tax Rate (Sales Taxes and Charges)', 'Total (Sales Taxes and Charges)', 
    'Total (Company Currency) (Sales Taxes and Charges)', 'Type (Sales Taxes and Charges)', 
    'Base Tax Withheld (Tax Withholding Entries)', 'Base Taxable Amount (Tax Withholding Entries)', 
    'Company (Tax Withholding Entries)', 'Created By Migration (Tax Withholding Entries)', 
    'Currency (Tax Withholding Entries)', 'Exchange Rate (Tax Withholding Entries)', 
    'Lower Deduction Certificate (Tax Withholding Entries)', 'Party (Tax Withholding Entries)', 
    'Party Type (Tax Withholding Entries)', 'Status (Tax Withholding Entries)', 
    'Tax ID (Tax Withholding Entries)', 'Tax Rate (Tax Withholding Entries)', 
    'Tax Withholding Category (Tax Withholding Entries)', 
    'Tax Withholding Group (Tax Withholding Entries)', 'Taxable Date (Tax Withholding Entries)', 
    'Taxable Document Name (Tax Withholding Entries)', 
    'Taxable Document Type (Tax Withholding Entries)', 
    'Under Withheld Reason (Tax Withholding Entries)', 
    'Withholding Date (Tax Withholding Entries)', 
    'Withholding Document Name (Tax Withholding Entries)', 
    'Withholding Document Type (Tax Withholding Entries)', 
    'Item Row (Item Wise Tax Details)', 'Tax Amount (Item Wise Tax Details)', 
    'Tax Rate (Item Wise Tax Details)', 'Tax Row (Item Wise Tax Details)', 
    'Taxable Amount (Item Wise Tax Details)', 'Child Docname (Pricing Rule Detail)', 
    'Item Code (Pricing Rule Detail)', 'Margin Type (Pricing Rule Detail)', 
    'Pricing Rule (Pricing Rule Detail)', 'Rate or Discount (Pricing Rule Detail)', 
    'Rule Applied (Pricing Rule Detail)', 'Actual Batch Quantity (Packed Items)', 
    'Actual Qty (Packed Items)', 'Batch No (Packed Items)', 
    'Conversion Factor (Packed Items)', 'Description (Packed Items)', 
    'From Warehouse (Packed Items)', 'Incoming Rate (Packed Items)', 
    'Item Code (Packed Items)', 'Item Name (Packed Items)', 'Ordered Qty (Packed Items)', 
    'Packed Qty (Packed Items)', 'Page Break (Packed Items)', 
    'Parent Detail docname (Packed Items)', 'Parent Item (Packed Items)', 
    'Picked Qty (Packed Items)', 'Prevdoc DocType (Packed Items)', 
    'Product Bundle (Packed Items)', 'Projected Qty (Packed Items)', 
    'Qty (Packed Items)', 'Rate (Packed Items)', 'Requested Qty (Packed Items)', 
    'Reserve Stock (Packed Items)', 'Serial and Batch Bundle (Packed Items)', 
    'Serial No (Packed Items)', 'Supplier delivers to Customer (Packed Items)', 
    'To Warehouse (Optional) (Packed Items)', 'UOM (Packed Items)', 
    'Use Serial No / Batch Fields (Packed Items)', 'Activity Type (Time Sheets)', 
    'Billing Amount (Time Sheets)', 'Billing Hours (Time Sheets)', 
    'Description (Time Sheets)', 'From Time (Time Sheets)', 'Project Name (Time Sheets)', 
    'Time Sheet (Time Sheets)', 'Timesheet Detail (Time Sheets)', 'To Time (Time Sheets)', 
    'Account (Sales Invoice Payment)', 'Amount (Sales Invoice Payment)', 
    'Base Amount (Company Currency) (Sales Invoice Payment)', 
    'Clearance Date (Sales Invoice Payment)', 'Default (Sales Invoice Payment)', 
    'Mode of Payment (Sales Invoice Payment)', 'Reference No (Sales Invoice Payment)', 
    'Type (Sales Invoice Payment)', 'Advance amount (Advances)', 
    'Allocated amount (Advances)', 'Difference Posting Date (Advances)', 
    'Exchange Gain/Loss (Advances)', 'Reference Exchange Rate (Advances)', 
    'Reference Name (Advances)', 'Reference Row (Advances)', 'Reference Type (Advances)', 
    'Remarks (Advances)', 'Credit Days (Payment Schedule)', 
    'Credit Months (Payment Schedule)', 'Description (Payment Schedule)', 
    'Discount (Payment Schedule)', 'Discount Date (Payment Schedule)', 
    'Discount Type (Payment Schedule)', 'Discount Validity (Payment Schedule)', 
    'Discount Validity Based On (Payment Schedule)', 
    'Discounted Amount (Payment Schedule)', 'Due Date (Payment Schedule)', 
    'Due Date Based On (Payment Schedule)', 'Invoice Portion (Payment Schedule)', 
    'Mode of Payment (Payment Schedule)', 'Outstanding (Payment Schedule)', 
    'Outstanding (Company Currency) (Payment Schedule)', 
    'Paid Amount (Payment Schedule)', 'Paid Amount (Company Currency) (Payment Schedule)', 
    'Payment Amount (Payment Schedule)', 
    'Payment Amount (Company Currency) (Payment Schedule)', 
    'Payment Term (Payment Schedule)', 
    'Commission Rate (Sales Contributions and Incentives)', 
    'Contact No. (Sales Contributions and Incentives)', 
    'Contribution (%) (Sales Contributions and Incentives)', 
    'Contribution to Net Total (Sales Contributions and Incentives)', 
    'Incentives (Sales Contributions and Incentives)', 
    'Sales Person (Sales Contributions and Incentives)'
]

class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def select_file(self, file_type):
        """Native Open/Save File Dialog"""
        if file_type == 'raw':
            res = self._window.create_file_dialog(FileDialog.OPEN, allow_multiple=False, file_types=('CSV Files (*.csv)', 'All files (*.*)'))
            return res[0] if res else ""
        elif file_type == 'erp':
            res = self._window.create_file_dialog(FileDialog.OPEN, allow_multiple=False, file_types=('CSV Files (*.csv)', 'All files (*.*)'))
            return res[0] if res else ""
        elif file_type == 'out':
            default_dir = os.path.abspath("cleaned_csv")
            os.makedirs(default_dir, exist_ok=True)
            res = self._window.create_file_dialog(FileDialog.SAVE, directory=default_dir, save_filename='Cleaned_Sales_Invoice.csv', file_types=('CSV Files (*.csv)',))
            return res if res else ""
        return ""

    def run_cleaning(self, config):
        try:
            raw_file = config.get('raw_file', '').strip()
            erp_mapping_file = config.get('erp_mapping_file', '').strip() or "ERP Code - Sheet1.csv"
            output_file = config.get('output_file', '').strip() or os.path.join("cleaned_csv", "Cleaned_Sales_Invoice.csv")

            if not raw_file or not os.path.exists(raw_file):
                return {'success': False, 'message': f"Raw file not found: {raw_file}"}

            out_dir = os.path.dirname(output_file)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            else:
                os.makedirs("cleaned_csv", exist_ok=True)
                output_file = os.path.join("cleaned_csv", output_file)

            # 1. Read ERP Mapping
            mapping_dict = {}
            if os.path.exists(erp_mapping_file):
                map_df = pd.read_csv(erp_mapping_file)
                for _, row in map_df.iterrows():
                    item_name = str(row['Items Name (Key)']).strip()
                    item_code = str(row['Item Code']).strip()
                    payment = str(row['Payment']).strip()
                    mapping_dict[item_name] = {'code': item_code, 'name': item_name, 'payment': payment}
                    mapping_dict[item_code] = {'code': item_code, 'name': item_name, 'payment': payment}

            # 2. Read Raw CSV
            with open(raw_file, mode='r', encoding='utf-8-sig', errors='ignore') as f:
                reader = list(csv.reader(f))

            invoices = []
            current_inv = None

            for row in reader:
                if not any(row):
                    continue
                row_str = " ".join(row)
                if "Docid :" in row_str:
                    if current_inv:
                        invoices.append(current_inv)
                    current_inv = {'header': [], 'items': [], 'summary': []}
                    current_inv['header'].append(row)
                elif current_inv is not None:
                    if any(k in row_str for k in ['Customer :', 'Location :', 'MemberCard :']):
                        current_inv['header'].append(row)
                    elif 'Code' in row[0] and 'Description' in row_str:
                        continue
                    elif any(k in row[0] for k in ['Member Discount', 'Tax', 'Invoice Total', 'Item Discount', 'Voucher Discount', 'Advance Pay', 'Paid Amount', 'Net Amount']):
                        current_inv['summary'].append(row)
                    else:
                        current_inv['items'].append(row)

            if current_inv:
                invoices.append(current_inv)

            final_rows = []

            for inv in invoices:
                invoice_no = ""
                date_str = ""
                customer = ""
                location = "SYS"

                for h_row in inv['header']:
                    for cell in h_row:
                        cell = cell.strip()
                        if cell.startswith("InvoiceNo :"):
                            invoice_no = cell.replace("InvoiceNo :", "").strip()
                        elif cell.startswith("Date :"):
                            raw_d = cell.replace("Date :", "").strip()
                            parts = raw_d.split('/')
                            if len(parts) == 3:
                                date_str = f"{int(parts[1]):02d}-{int(parts[0]):02d}-{parts[2]}"
                            else:
                                date_str = raw_d
                        elif cell.startswith("Customer :"):
                            customer = cell.replace("Customer :", "").strip()
                        elif cell.startswith("Location :"):
                            location = cell.replace("Location :", "").strip()

                customer_display = "Temporary" if (customer == "Customer" or not customer) else customer

                first_item = True
                for it in inv['items']:
                    final_item_code = ""
                    item_name = ""
                    matched_info = None

                    for cell in it:
                        c_clean = cell.strip()
                        if c_clean in mapping_dict:
                            matched_info = mapping_dict[c_clean]
                            final_item_code = matched_info['code']
                            item_name = matched_info['name']
                            if c_clean != final_item_code:
                                break

                    if not final_item_code:
                        continue

                    num_cells = []
                    for cell in it:
                        c = cell.strip().replace(',', '')
                        if c != "" and (c.isdigit() or (c.replace('.', '', 1).isdigit() and '.' in c)):
                            num_cells.append(cell.strip().replace(',', ''))

                    qty = 1
                    rate = 0
                    if len(num_cells) >= 2:
                        qty = int(float(num_cells[0]))
                        rate = int(float(num_cells[1]))
                    elif len(num_cells) == 1:
                        qty = int(float(num_cells[0]))

                    amount = qty * rate

                    if str(final_item_code).startswith("INT-"):
                        source_warehouse = f"{location} (Interest) MMK - SYS"
                    else:
                        payment_type = matched_info['payment'] if matched_info else "USD"
                        source_warehouse = f"{payment_type} {location} - SYS"

                    is_free = 1 if rate == 0 else 0

                    # 360-column record dictionary initialization
                    row_data = {col: "" for col in SALES_INVOICE_COLUMNS}

                    # Header Columns (Only on First Item of Invoice)
                    if first_item:
                        row_data['Company'] = config.get('company', 'Seinn Yaung So')
                        row_data['Series'] = config.get('series', 'ACC-SINV-.YYYY.-')
                        row_data['Customer'] = customer_display
                        row_data['Posting Date'] = date_str
                        row_data['Currency'] = config.get('currency', 'MMK')
                        row_data['Exchange Rate'] = float(config.get('exchange_rate', '1.0'))
                        row_data['Price List'] = config.get('price_list', 'Standard Selling')
                        row_data['Price List Currency'] = config.get('price_list_currency', 'MMK')
                        row_data['Price List Exchange Rate'] = float(config.get('price_list_exchange_rate', '1.0'))
                        row_data['Update Stock'] = 1.0
                        row_data['Is Opening Entry'] = 'No'
                        row_data['Remarks'] = invoice_no

                    # Child Item Columns
                    row_data['Item (Items)'] = final_item_code
                    row_data['Item Name (Items)'] = item_name
                    row_data['Description (Items)'] = item_name
                    row_data['Quantity (Items)'] = qty
                    row_data['Rate (Items)'] = rate
                    row_data['Rate (Company Currency) (Items)'] = rate
                    row_data['Price List Rate (Items)'] = rate
                    row_data['Price List Rate (Company Currency) (Items)'] = rate
                    row_data['Net Rate (Items)'] = rate
                    row_data['Net Rate (Company Currency) (Items)'] = rate
                    row_data['Amount (Items)'] = amount
                    row_data['Amount (Company Currency) (Items)'] = amount
                    row_data['Net Amount (Items)'] = amount
                    row_data['Net Amount (Company Currency) (Items)'] = amount
                    row_data['UOM (Items)'] = config.get('uom', 'Nos')
                    row_data['Stock UOM (Items)'] = config.get('uom', 'Nos')
                    row_data['UOM Conversion Factor (Items)'] = int(config.get('uom_conv', '1'))
                    row_data['Cost Center (Items)'] = config.get('cost_center', 'Main - SYS')
                    row_data['Allow Zero Valuation Rate (Items)'] = 1
                    row_data['Grant Commission (Items)'] = 1
                    row_data['Is Free Item (Items)'] = is_free
                    row_data['Warehouse (Items)'] = source_warehouse
                    row_data['Target Warehouse (Items)'] = source_warehouse

                    final_rows.append(row_data)
                    first_item = False

            # Export to CSV with full 360-column standard layout
            with open(output_file, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=SALES_INVOICE_COLUMNS)
                writer.writeheader()
                writer.writerows(final_rows)

            return {
                'success': True,
                'total_invoices': len(invoices),
                'total_items': len(final_rows),
                'output_file': os.path.abspath(output_file)
            }

        except Exception as e:
            return {'success': False, 'message': str(e)}

# Modern Web UI Layout
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ERP Sales Invoice Cleaner</title>
    <style>
        :root {
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text-main); padding: 24px; }
        .container { max-width: 820px; margin: 0 auto; }
        .header { margin-bottom: 20px; }
        .header h1 { font-size: 22px; font-weight: 700; color: var(--text-main); }
        .header p { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
        
        .card { background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border); padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card-title { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 14px; }
        
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; }
        .input-row { display: flex; gap: 8px; }
        input[type="text"] { flex: 1; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; outline: none; transition: border 0.2s; }
        input[type="text"]:focus { border-color: var(--primary); }
        
        .btn-browse { padding: 8px 14px; background: #f1f5f9; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; }
        .btn-browse:hover { background: #e2e8f0; }

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

        .btn-primary { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        .btn-primary:hover { background: var(--primary-hover); }

        .log-box { margin-top: 12px; padding: 12px; background: #0f172a; color: #38bdf8; border-radius: 6px; font-family: monospace; font-size: 12px; min-height: 70px; max-height: 140px; overflow-y: auto; white-space: pre-line; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ERP Sales Invoice Data Cleaner</h1>
            <p>Clean raw invoice exports and transform into full ERPNext Sales Invoice import format</p>
        </div>

        <div class="card">
            <div class="card-title">File Selection</div>
            <div class="form-group">
                <label>Raw CSV File</label>
                <div class="input-row">
                    <input type="text" id="raw_file" placeholder="Select uncleaned raw CSV file (e.g. Sale Invoice (Feb to June) - 4 April.csv)...">
                    <button class="btn-browse" onclick="browseFile('raw')">Browse</button>
                </div>
            </div>
            <div class="form-group">
                <label>ERP Mapping File</label>
                <div class="input-row">
                    <input type="text" id="erp_mapping_file" value="ERP Code - Sheet1.csv">
                    <button class="btn-browse" onclick="browseFile('erp')">Browse</button>
                </div>
            </div>
            <div class="form-group">
                <label>Output CSV File (Saved in <code>cleaned_csv/</code>)</label>
                <div class="input-row">
                    <input type="text" id="output_file" value="cleaned_csv/SYS2_Import_Sales_Invoice_April2026_FULL.csv">
                    <button class="btn-browse" onclick="browseFile('out')">Save As</button>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Configuration & Parameters</div>
            <div class="grid-2">
                <div class="form-group"><label>Series</label><input type="text" id="series" value="ACC-SINV-.YYYY.-"></div>
                <div class="form-group"><label>Company Name</label><input type="text" id="company" value="Seinn Yaung So"></div>
                <div class="form-group"><label>Cost Center (Items)</label><input type="text" id="cost_center" value="Main - SYS"></div>
                <div class="form-group"><label>Currency</label><input type="text" id="currency" value="MMK"></div>
                <div class="form-group"><label>Exchange Rate</label><input type="text" id="exchange_rate" value="1.0"></div>
                <div class="form-group"><label>Price List</label><input type="text" id="price_list" value="Standard Selling"></div>
                <div class="form-group"><label>Price List Currency</label><input type="text" id="price_list_currency" value="MMK"></div>
                <div class="form-group"><label>Price List Ex. Rate</label><input type="text" id="price_list_exchange_rate" value="1.0"></div>
                <div class="form-group"><label>UOM (Items)</label><input type="text" id="uom" value="Nos"></div>
                <div class="form-group"><label>UOM Conv Factor</label><input type="text" id="uom_conv" value="1"></div>
            </div>
        </div>

        <button class="btn-primary" onclick="runCleaner()">⚡ Start Data Cleaning</button>

        <div class="log-box" id="logBox">Ready to process...</div>
    </div>

    <script>
        function log(msg) {
            const box = document.getElementById('logBox');
            box.innerText = msg;
        }

        async function browseFile(type) {
            const res = await pywebview.api.select_file(type);
            if (res) {
                if (type === 'raw') document.getElementById('raw_file').value = res;
                if (type === 'erp') document.getElementById('erp_mapping_file').value = res;
                if (type === 'out') document.getElementById('output_file').value = res;
            }
        }

        async function runCleaner() {
            const rawFile = document.getElementById('raw_file').value.trim();
            if (!rawFile) {
                alert("Please select a Raw CSV file first.");
                return;
            }

            const config = {
                raw_file: rawFile,
                erp_mapping_file: document.getElementById('erp_mapping_file').value.trim(),
                output_file: document.getElementById('output_file').value.trim(),
                series: document.getElementById('series').value.trim(),
                company: document.getElementById('company').value.trim(),
                cost_center: document.getElementById('cost_center').value.trim(),
                currency: document.getElementById('currency').value.trim(),
                exchange_rate: document.getElementById('exchange_rate').value.trim(),
                price_list: document.getElementById('price_list').value.trim(),
                price_list_currency: document.getElementById('price_list_currency').value.trim(),
                price_list_exchange_rate: document.getElementById('price_list_exchange_rate').value.trim(),
                uom: document.getElementById('uom').value.trim(),
                uom_conv: document.getElementById('uom_conv').value.trim()
            };

            log("Processing... Please wait.");
            const res = await pywebview.api.run_cleaning(config);
            if (res.success) {
                log(`✔ [SUCCESS] Processed ${res.total_invoices} invoices (${res.total_items} items).\\nOutput File: ${res.output_file}`);
                alert(`Success!\\nCleaned File: ${res.output_file}\\nTotal Invoices: ${res.total_invoices}`);
            } else {
                log(`❌ [ERROR] ${res.message}`);
                alert("Error: " + res.message);
            }
        }
    </script>
</body>
</html>
"""

def main():
    api = Api()
    window = webview.create_window(
        title='ERP Sales Invoice Cleaning Tool',
        html=HTML_UI,
        js_api=api,
        width=850,
        height=720,
        resizable=True
    )
    api.set_window(window)
    webview.start()

if __name__ == '__main__':
    main()