import os
import csv
import re
import webview
from webview import FileDialog
import pandas as pd

def parse_custom_id(id_str):
    match = re.search(r'^(.*?)(\d+)$', id_str)
    if match:
        prefix = match.group(1)
        num_str = match.group(2)
        pad_len = len(num_str)
        start_num = int(num_str)
        return prefix, start_num, pad_len
    return id_str + "-", 1, 5

class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def select_file(self, file_type):
        """Native Open/Save File Dialog with modern FileDialog API"""
        if file_type == 'raw':
            res = self._window.create_file_dialog(FileDialog.OPEN, allow_multiple=False, file_types=('CSV Files (*.csv)', 'All files (*.*)'))
            return res[0] if res else ""
        elif file_type == 'erp':
            res = self._window.create_file_dialog(FileDialog.OPEN, allow_multiple=False, file_types=('CSV Files (*.csv)', 'All files (*.*)'))
            return res[0] if res else ""
        elif file_type == 'out':
            # Default save to cleaned_csv folder
            default_dir = os.path.abspath("cleaned_csv")
            os.makedirs(default_dir, exist_ok=True)
            res = self._window.create_file_dialog(FileDialog.SAVE, directory=default_dir, save_filename='Cleaned_Sales_Order.csv', file_types=('CSV Files (*.csv)',))
            return res if res else ""
        return ""

    def run_cleaning(self, config):
        try:
            raw_file = config.get('raw_file', '').strip()
            erp_mapping_file = config.get('erp_mapping_file', '').strip() or "ERP Code - Sheet1.csv"
            output_file = config.get('output_file', '').strip() or os.path.join("cleaned_csv", "Cleaned_Sales_Order.csv")

            if not raw_file or not os.path.exists(raw_file):
                return {'success': False, 'message': f"Raw file not found: {raw_file}"}

            # cleaned_csv folder မရှိပါက auto ဆောက်ပေးခြင်း
            out_dir = os.path.dirname(output_file)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            else:
                os.makedirs("cleaned_csv", exist_ok=True)
                output_file = os.path.join("cleaned_csv", output_file)

            # 1. Parse ID
            start_id_str = config.get('start_id_str', '').strip() or "SAL-ORD-2026-00356"
            id_prefix, curr_id_num, pad_len = parse_custom_id(start_id_str)

            # 2. Read ERP Mapping
            mapping_dict = {}
            if os.path.exists(erp_mapping_file):
                map_df = pd.read_csv(erp_mapping_file)
                for _, row in map_df.iterrows():
                    item_name = str(row['Items Name (Key)']).strip()
                    item_code = str(row['Item Code']).strip()
                    payment = str(row['Payment']).strip()
                    mapping_dict[item_name] = {'code': item_code, 'payment': payment}
                    mapping_dict[item_code] = {'code': item_code, 'payment': payment}

            # 3. Read Raw CSV
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
                                date_str = f"{parts[1]}-{parts[0]}-{parts[2]}"
                            else:
                                date_str = raw_d
                        elif cell.startswith("Customer :"):
                            customer = cell.replace("Customer :", "").strip()
                        elif cell.startswith("Location :"):
                            location = cell.replace("Location :", "").strip()

                customer_display = "Temporary" if (customer == "Customer" or not customer) else customer

                voucher_discount = ""
                for s_row in inv['summary']:
                    if len(s_row) > 0 and s_row[0].strip() == "Voucher Discount":
                        disc_vals = [c.strip() for c in s_row[1:] if c.strip() != ""]
                        if disc_vals:
                            voucher_discount = disc_vals[-1]

                first_item = True
                for it in inv['items']:
                    final_item_code = ""
                    matched_info = None

                    for cell in it:
                        c_clean = cell.strip()
                        if c_clean in mapping_dict:
                            matched_info = mapping_dict[c_clean]
                            final_item_code = matched_info['code']
                            if c_clean != final_item_code:
                                break

                    if not final_item_code:
                        continue

                    num_cells = []
                    for cell in it:
                        c = cell.strip().replace(',', '')
                        if c != "" and (c.isdigit() or (c.replace('.', '', 1).isdigit() and '.' in c)):
                            num_cells.append(cell.strip())

                    qty = "1"
                    rate = "0"
                    if len(num_cells) >= 2:
                        qty = num_cells[0]
                        rate = num_cells[1]
                    elif len(num_cells) == 1:
                        qty = num_cells[0]

                    if str(final_item_code).startswith("INT-"):
                        source_warehouse = f"{location} (Interest) MMK - SYS"
                    else:
                        payment_type = matched_info['payment'] if matched_info else "USD"
                        source_warehouse = f"{payment_type} {location} - SYS"

                    formatted_id = f"{id_prefix}{str(curr_id_num).zfill(pad_len)}"

                    row_data = {
                        'ID': formatted_id if first_item else "",
                        'Company': config.get('company', 'Seinn Yaung So') if first_item else "",
                        'Series': config.get('series', 'SAL-ORD-.YYYY.-') if first_item else "",
                        'Customer': customer_display if first_item else "",
                        'Order Type': config.get('order_type', 'Sales') if first_item else "",
                        'Date': date_str if first_item else "",
                        'Currency': config.get('currency', 'MMK') if first_item else "",
                        'Exchange Rate': config.get('exchange_rate', '1.0') if first_item else "",
                        'Price List': config.get('price_list', 'Standard Selling') if first_item else "",
                        'Price List Currency': config.get('price_list_currency', 'MMK') if first_item else "",
                        'Price List Exchange Rate': config.get('price_list_exchange_rate', '1.0') if first_item else "",
                        'Status': config.get('status', 'To Deliver and Bill') if first_item else "",
                        'Remark': invoice_no if first_item else "",
                        'Customer Name': customer_display if first_item else "",
                        'Delivery Date': config.get('delivery_date', '30-6-2026') if first_item else "",
                        'Item Code (Items)': final_item_code,
                        'Quantity (Items)': qty,
                        'UOM (Items)': config.get('uom', 'Nos'),
                        'UOM Conversion Factor (Items)': config.get('uom_conv', '1'),
                        'Source Warehouse (Items)': source_warehouse,
                        'Rate (Items)': rate,
                        'Additional Discount Amount': voucher_discount if first_item else ""
                    }
                    final_rows.append(row_data)
                    first_item = False

                if not first_item:
                    curr_id_num += 1

            fieldnames = [
                'ID', 'Company', 'Series', 'Customer', 'Order Type', 'Date',
                'Currency', 'Exchange Rate', 'Price List', 'Price List Currency',
                'Price List Exchange Rate', 'Status', 'Remark', 'Customer Name',
                'Delivery Date', 'Item Code (Items)', 'Quantity (Items)', 'UOM (Items)',
                'UOM Conversion Factor (Items)', 'Source Warehouse (Items)',
                'Rate (Items)', 'Additional Discount Amount'
            ]

            with open(output_file, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(final_rows)

            last_id = f"{id_prefix}{str(curr_id_num - 1).zfill(pad_len)}"
            return {
                'success': True,
                'total_invoices': len(invoices),
                'output_file': os.path.abspath(output_file),
                'last_id': last_id
            }

        except Exception as e:
            return {'success': False, 'message': str(e)}

# Modern Web UI Layout
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ERP Data Cleaner</title>
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
            <h1>ERP Sales Order Data Cleaner</h1>
            <p>Clean raw invoices and export directly into ERPNext format</p>
        </div>

        <div class="card">
            <div class="card-title">File Selection</div>
            <div class="form-group">
                <label>Raw CSV File</label>
                <div class="input-row">
                    <input type="text" id="raw_file" placeholder="Select uncleaned raw CSV file...">
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
                <label>Output CSV File (Saved into <code>cleaned_csv/</code>)</label>
                <div class="input-row">
                    <input type="text" id="output_file" value="cleaned_csv/Cleaned_Sales_Order.csv">
                    <button class="btn-browse" onclick="browseFile('out')">Save As</button>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Configuration & Parameters</div>
            <div class="grid-2">
                <div class="form-group"><label>Starting ID</label><input type="text" id="start_id_str" value="SAL-ORD-2026-00356"></div>
                <div class="form-group"><label>Series</label><input type="text" id="series" value="SAL-ORD-.YYYY.-"></div>
                <div class="form-group"><label>Company Name</label><input type="text" id="company" value="Seinn Yaung So"></div>
                <div class="form-group"><label>Order Type</label><input type="text" id="order_type" value="Sales"></div>
                <div class="form-group"><label>Currency</label><input type="text" id="currency" value="MMK"></div>
                <div class="form-group"><label>Exchange Rate</label><input type="text" id="exchange_rate" value="1.0"></div>
                <div class="form-group"><label>Price List</label><input type="text" id="price_list" value="Standard Selling"></div>
                <div class="form-group"><label>Price List Currency</label><input type="text" id="price_list_currency" value="MMK"></div>
                <div class="form-group"><label>Status</label><input type="text" id="status" value="To Deliver and Bill"></div>
                <div class="form-group"><label>Delivery Date</label><input type="text" id="delivery_date" value="30-6-2026"></div>
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
                start_id_str: document.getElementById('start_id_str').value.trim(),
                series: document.getElementById('series').value.trim(),
                company: document.getElementById('company').value.trim(),
                order_type: document.getElementById('order_type').value.trim(),
                currency: document.getElementById('currency').value.trim(),
                exchange_rate: document.getElementById('exchange_rate').value.trim(),
                price_list: document.getElementById('price_list').value.trim(),
                price_list_currency: document.getElementById('price_list_currency').value.trim(),
                status: document.getElementById('status').value.trim(),
                delivery_date: document.getElementById('delivery_date').value.trim(),
                uom: document.getElementById('uom').value.trim(),
                uom_conv: document.getElementById('uom_conv').value.trim()
            };

            log("Processing... Please wait.");
            const res = await pywebview.api.run_cleaning(config);
            if (res.success) {
                log(`✔ [SUCCESS] Processed ${res.total_invoices} invoices.\\nOutput File: ${res.output_file}\\nLast ID Generated: ${res.last_id}`);
                alert(`Success!\\nSaved to: ${res.output_file}\\nLast ID: ${res.last_id}`);
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
        title='ERP Sales Order Cleaning Tool',
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