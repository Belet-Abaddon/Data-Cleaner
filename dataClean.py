import os
import csv
import json
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

IGNORE_SUMMARY_KEYWORDS = [
    'Customer :', 'Location :', 'MemberCard :', 'Docid :', 'Payment :',
    'Member Discount', 'Tax', 'Invoice Total', 'Item Discount', 'Voucher Discount', 
    'Advance Pay', 'Paid Amount', 'Net Amount', 'Total Amount', 'Total Item Discount', 
    'Total VouDiscount', 'Total Tax', 'Total AdvancePay', 'Total Paid'
]

def load_erp_mapping(erp_mapping_file):
    mapping_dict = {}
    erp_items = []
    if os.path.exists(erp_mapping_file):
        try:
            map_df = pd.read_csv(erp_mapping_file, on_bad_lines='skip', encoding='utf-8-sig')
            for _, row in map_df.iterrows():
                code = str(row.get('Item Code', '')).strip()
                name = str(row.get('Items Name (Key)', '')).strip()
                payment = str(row.get('Payment', 'USD')).strip()
                if code and name and code != 'nan' and name != 'nan':
                    mapping_dict[name] = {'code': code, 'name': name, 'payment': payment}
                    mapping_dict[code] = {'code': code, 'name': name, 'payment': payment}
                    erp_items.append({'code': code, 'name': name, 'payment': payment})
        except Exception as e:
            print(f"Error loading mapping CSV: {e}")
    return mapping_dict, erp_items

def parse_invoices_from_raw(raw_file):
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
            current_inv = {'header': [row], 'items': [], 'summary': []}
        elif current_inv is not None:
            if any(k in row_str for k in ['Customer :', 'Location :', 'MemberCard :', 'Payment :']):
                current_inv['header'].append(row)
            elif 'Code' in row[0] and 'Description' in row_str:
                continue
            elif any(k in row_str for k in IGNORE_SUMMARY_KEYWORDS):
                current_inv['summary'].append(row)
            else:
                current_inv['items'].append(row)
    if current_inv:
        invoices.append(current_inv)

    return invoices

class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def select_file(self, file_type):
        if file_type in ['raw', 'erp']:
            res = self._window.create_file_dialog(FileDialog.OPEN, allow_multiple=False, file_types=('CSV Files (*.csv)', 'All files (*.*)'))
            return res[0] if res else ""
        elif file_type == 'out':
            default_dir = os.path.abspath("cleaned_csv")
            os.makedirs(default_dir, exist_ok=True)
            res = self._window.create_file_dialog(FileDialog.SAVE, directory=default_dir, save_filename='Cleaned_Sales_Invoice.csv', file_types=('CSV Files (*.csv)',))
            return res if res else ""
        return ""

    def check_unmapped_items(self, raw_file, erp_mapping_file):
        """Scan raw CSV and extract context-rich unmapped items with remark suggestions"""
        try:
            if not os.path.exists(raw_file):
                return {'success': False, 'message': 'Raw file not found'}
            
            erp_mapping_file = erp_mapping_file or "ERP Code - Sheet1.csv"
            mapping_dict, erp_items = load_erp_mapping(erp_mapping_file)
            invoices = parse_invoices_from_raw(raw_file)

            unmapped_list = []

            for inv_idx, inv in enumerate(invoices):
                invoice_no = ""
                customer = ""
                remark = ""

                for h_row in inv['header']:
                    for cell in h_row:
                        cell_s = cell.strip()
                        if cell_s.startswith("InvoiceNo :"):
                            invoice_no = cell_s.replace("InvoiceNo :", "").strip()
                        elif cell_s.startswith("Customer :"):
                            customer = cell_s.replace("Customer :", "").strip()
                        elif cell_s.startswith("Remark :") or "Remark :" in cell_s:
                            remark = cell_s[cell_s.find("Remark :") + 8:].strip()

                for item_idx, it in enumerate(inv['items']):
                    found = False
                    for cell in it:
                        c_clean = cell.strip()
                        if c_clean in mapping_dict:
                            found = True
                            break
                    if not found:
                        valid_cells = [c.strip() for c in it if c.strip()]
                        if valid_cells:
                            if any(k in valid_cells[0] for k in IGNORE_SUMMARY_KEYWORDS):
                                continue

                            raw_code = valid_cells[0]
                            raw_name = valid_cells[1] if len(valid_cells) > 1 else valid_cells[0]
                            amount = valid_cells[-1] if len(valid_cells) > 2 else ""

                            # Smart Auto-Suggestion based on Remark
                            suggested_code = ""
                            rem_lower = (remark + " " + raw_name).lower()
                            if "12 month" in rem_lower or "12 လ" in rem_lower:
                                suggested_code = "INT-4"
                            elif "6 month" in rem_lower or "6 လ" in rem_lower:
                                suggested_code = "INT-1"
                            elif "8 month" in rem_lower or "8 လ" in rem_lower:
                                suggested_code = "INT-2"
                            elif "3 month" in rem_lower or "3 လ" in rem_lower:
                                suggested_code = "INT-3"
                            elif "7 month" in rem_lower or "7 လ" in rem_lower:
                                suggested_code = "INT-5"
                            elif "9 month" in rem_lower or "9 လ" in rem_lower:
                                suggested_code = "INT-6"
                            elif "1 month" in rem_lower or "1 လ" in rem_lower:
                                suggested_code = "INT-7"
                            elif "2 month" in rem_lower or "2 လ" in rem_lower:
                                suggested_code = "INT-8"

                            unmapped_list.append({
                                'id': f"{inv_idx}_{item_idx}",
                                'invoice_no': invoice_no,
                                'customer': customer,
                                'remark': remark,
                                'raw_code': raw_code,
                                'raw_name': raw_name,
                                'amount': amount,
                                'suggested_code': suggested_code
                            })

            return {
                'success': True,
                'unmapped_count': len(unmapped_list),
                'unmapped_items': unmapped_list,
                'erp_options': erp_items
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def run_cleaning(self, config, custom_mappings=None):
        try:
            raw_file = config.get('raw_file', '').strip()
            erp_mapping_file = config.get('erp_mapping_file', '').strip() or "ERP Code - Sheet1.csv"
            output_file = config.get('output_file', '').strip() or os.path.join("cleaned_csv", "Cleaned_Sales_Invoice.csv")

            if not raw_file or not os.path.exists(raw_file):
                return {'success': False, 'message': f"Raw file not found: {raw_file}"}

            out_dir = os.path.dirname(output_file)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            mapping_dict, _ = load_erp_mapping(erp_mapping_file)
            invoices = parse_invoices_from_raw(raw_file)

            custom_map_by_id = {}
            if custom_mappings and isinstance(custom_mappings, list):
                for m in custom_mappings:
                    row_id = m.get('id')
                    if row_id:
                        custom_map_by_id[row_id] = {
                            'code': m.get('selected_code'),
                            'name': m.get('selected_name'),
                            'payment': m.get('selected_payment', 'MMK')
                        }

            final_rows = []

            for inv_idx, inv in enumerate(invoices):
                invoice_no = ""
                date_str = ""
                customer = ""
                location = "SYS"
                voucher_discount = ""

                for h_row in inv['header']:
                    for cell in h_row:
                        cell_s = cell.strip()
                        if cell_s.startswith("InvoiceNo :"):
                            invoice_no = cell_s.replace("InvoiceNo :", "").strip()
                        elif cell_s.startswith("Date :"):
                            raw_d = cell_s.replace("Date :", "").strip()
                            parts = raw_d.split('/')
                            if len(parts) == 3:
                                date_str = f"{int(parts[1]):02d}-{int(parts[0]):02d}-{parts[2]}"
                            else:
                                date_str = raw_d
                        elif cell_s.startswith("Customer :"):
                            customer = cell_s.replace("Customer :", "").strip()
                        elif cell_s.startswith("Location :"):
                            location = cell_s.replace("Location :", "").strip()

                # Extract Voucher Discount from Invoice Summary rows
                for s_row in inv['summary']:
                    s_row_str = " ".join(s_row)
                    if "Voucher Discount" in s_row[0] or "Voucher Discount" in s_row_str:
                        for cell in s_row:
                            c = cell.strip().replace(',', '')
                            if c != "" and (c.isdigit() or (c.replace('.', '', 1).isdigit() and '.' in c)):
                                voucher_discount = int(float(c))
                                break

                customer_display = "Temporary" if (customer == "Customer" or not customer) else customer

                first_item = True
                for item_idx, it in enumerate(inv['items']):
                    row_key_id = f"{inv_idx}_{item_idx}"
                    final_item_code = ""
                    item_name = ""
                    matched_info = None

                    if row_key_id in custom_map_by_id:
                        matched_info = custom_map_by_id[row_key_id]
                        final_item_code = matched_info['code']
                        item_name = matched_info['name']
                    else:
                        for cell in it:
                            c_clean = cell.strip()
                            if c_clean in mapping_dict:
                                matched_info = mapping_dict[c_clean]
                                final_item_code = matched_info['code']
                                item_name = matched_info['name']
                                break

                    if not final_item_code:
                        continue

                    num_cells = []
                    for cell in it:
                        c = cell.strip().replace(',', '')
                        if c != "" and (c.isdigit() or (c.replace('.', '', 1).isdigit() and '.' in c)):
                            num_cells.append(c)

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

                    row_data = {col: "" for col in SALES_INVOICE_COLUMNS}

                    # Header Columns on First Item of Invoice
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
                        
                        # Voucher Discount placed in Additional Discount Amount
                        if voucher_discount != "":
                            row_data['Additional Discount Amount'] = voucher_discount

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
        .container { max-width: 860px; margin: 0 auto; }
        .header { margin-bottom: 20px; }
        .header h1 { font-size: 22px; font-weight: 700; color: var(--text-main); }
        .header p { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
        
        .card { background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border); padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card-title { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 14px; }
        
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; }
        .input-row { display: flex; gap: 8px; }
        input[type="text"], select { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; outline: none; transition: border 0.2s; }
        input[type="text"]:focus, select:focus { border-color: var(--primary); }
        
        .btn-browse { padding: 8px 14px; background: #f1f5f9; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; white-space: nowrap; }
        .btn-browse:hover { background: #e2e8f0; }

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

        .btn-primary { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        .btn-primary:hover { background: var(--primary-hover); }

        .log-box { margin-top: 12px; padding: 12px; background: #0f172a; color: #38bdf8; border-radius: 6px; font-family: monospace; font-size: 12px; min-height: 70px; max-height: 140px; overflow-y: auto; white-space: pre-line; }

        /* Modal Popup */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; }
        .modal-content { background: #fff; width: 95%; max-width: 900px; max-height: 88vh; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }
        .modal-body { overflow-y: auto; flex: 1; margin-bottom: 16px; padding-right: 6px; }
        
        .mapping-card { padding: 12px; background: #f8fafc; border-radius: 8px; margin-bottom: 10px; border: 1px solid var(--border); }
        .mapping-header { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
        .mapping-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: center; }
        .remark-box { font-size: 11.5px; background: #fff; padding: 6px 8px; border-radius: 4px; border: 1px dashed #cbd5e1; color: #334155; margin-top: 4px; }
        .modal-footer { display: flex; justify-content: flex-end; gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ERP Sales Invoice Data Cleaner</h1>
            <p>Clean raw invoice exports with automated interactive mapping & remark context</p>
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
                <label>Output CSV File</label>
                <div class="input-row">
                    <input type="text" id="output_file" value="cleaned_csv/Cleaned_Sales_Invoice.csv">
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

        <button class="btn-primary" onclick="startProcess()">⚡ Start Data Cleaning</button>

        <div class="log-box" id="logBox">Ready to process...</div>
    </div>

    <!-- Interactive Mapping Modal with Remark Context -->
    <div class="modal" id="mapModal">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <h3 style="font-size: 16px; font-weight: 700;">Unmapped Items Detected</h3>
                    <p style="font-size: 12px; color: var(--text-muted);">Review invoice remarks and map to the corresponding ERP item rate:</p>
                </div>
            </div>
            <div class="modal-body" id="mappingList"></div>
            <div class="modal-footer">
                <button class="btn-browse" onclick="closeModal()">Skip & Ignore</button>
                <button class="btn-primary" style="width: auto; padding: 8px 20px;" onclick="applyMappingsAndRun()">Save & Continue Cleaning</button>
            </div>
        </div>
    </div>

    <script>
        let currentConfig = {};
        let cachedUnmappedItems = [];
        let cachedErpOptions = [];

        function log(msg) {
            document.getElementById('logBox').innerText = msg;
        }

        async function browseFile(type) {
            const res = await pywebview.api.select_file(type);
            if (res) {
                if (type === 'raw') document.getElementById('raw_file').value = res;
                if (type === 'erp') document.getElementById('erp_mapping_file').value = res;
                if (type === 'out') document.getElementById('output_file').value = res;
            }
        }

        function getFormConfig() {
            return {
                raw_file: document.getElementById('raw_file').value.trim(),
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
        }

        async function startProcess() {
            currentConfig = getFormConfig();
            if (!currentConfig.raw_file) {
                alert("Please select a Raw CSV file first.");
                return;
            }

            log("Scanning raw file for unmapped items & checking remarks...");
            const scan = await pywebview.api.check_unmapped_items(currentConfig.raw_file, currentConfig.erp_mapping_file);
            
            if (scan.success && scan.unmapped_count > 0) {
                cachedUnmappedItems = scan.unmapped_items;
                cachedErpOptions = scan.erp_options;
                showMappingModal(cachedUnmappedItems, cachedErpOptions);
            } else {
                executeCleaning([]);
            }
        }

        function showMappingModal(unmapped, erpOptions) {
            const list = document.getElementById('mappingList');
            list.innerHTML = "";

            unmapped.forEach((item) => {
                let optionsHtml = `<option value="">-- Ignore this item --</option>`;
                erpOptions.forEach(opt => {
                    const isSelected = (item.suggested_code === opt.code) ? "selected" : "";
                    optionsHtml += `<option value="${opt.code}" data-name="${opt.name}" data-payment="${opt.payment}" ${isSelected}>${opt.code} | ${opt.name} (${opt.payment})</option>`;
                });

                const card = document.createElement('div');
                card.className = 'mapping-card';
                card.innerHTML = `
                    <div class="mapping-header">
                        <span><strong>Inv:</strong> ${item.invoice_no || 'N/A'} | <strong>Customer:</strong> ${item.customer || 'Temporary'}</span>
                        <span style="color: #047857; font-weight: 600;">Amount: ${item.amount} MMK</span>
                    </div>
                    <div class="mapping-grid">
                        <div>
                            <div style="font-size: 13px; font-weight: 600; color: #b91c1c;">${item.raw_name} <span style="font-size:11px; color:#64748b;">(${item.raw_code})</span></div>
                            <div class="remark-box" title="${item.remark}"><strong>Remark:</strong> ${item.remark ? item.remark : '<em>No remark provided</em>'}</div>
                        </div>
                        <div>
                            <label style="font-size: 11px; color: #64748b; margin-bottom: 2px; display: block;">Select ERP Standard Item:</label>
                            <select id="map_select_${item.id}">
                                ${optionsHtml}
                            </select>
                        </div>
                    </div>
                `;
                list.appendChild(card);
            });

            document.getElementById('mapModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('mapModal').style.display = 'none';
            executeCleaning([]);
        }

        async function applyMappingsAndRun() {
            const mappings = [];
            cachedUnmappedItems.forEach((item) => {
                const sel = document.getElementById(`map_select_${item.id}`);
                if (sel && sel.value) {
                    const selectedOpt = sel.options[sel.selectedIndex];
                    mappings.push({
                        id: item.id,
                        selected_code: sel.value,
                        selected_name: selectedOpt.getAttribute('data-name'),
                        selected_payment: selectedOpt.getAttribute('data-payment')
                    });
                }
            });

            document.getElementById('mapModal').style.display = 'none';
            executeCleaning(mappings);
        }

        async function executeCleaning(mappings) {
            log("Processing Sales Invoice cleaning... Please wait.");
            const res = await pywebview.api.run_cleaning(currentConfig, mappings);
            if (res.success) {
                log(`✔ [SUCCESS] Processed ${res.total_invoices} invoices (${res.total_items} items).\\nOutput File: ${res.output_file}`);
                alert(`Success!\\nCleaned File: ${res.output_file}\\nTotal Invoices: ${res.total_invoices}\\nTotal Items: ${res.total_items}`);
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
        width=920,
        height=760,
        resizable=True
    )
    api.set_window(window)
    webview.start()

if __name__ == '__main__':
    main()