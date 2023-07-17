import datetime
import frappe
def execute(filters=None):
    conditions,select_fields= get_conditions(filters)
    columns, data = [], []
    columns = [ {
                "label": "Invoice No",
                "fieldname": "name",
                "fieldtype": "Link",
                "options": "Purchase Invoice",
                "width": 120
                },
                {
                "label": "Status",
                "fieldname": "status",
                "fieldtype": "Select",
                "options": [
                        "Draft",
                        "Return",
                        "Debit Note Issued",
                        "Submitted",
                        "Paid",
                        "Partly Paid",
                        "Unpaid",
                        "Overdue",
                        "Cancelled",
                        "Internal Transfer"],
                
                "width": 120
                },
                

                {
                "label": "Date",
                "fieldname": "posting_date",
                "fieldtype": "Link",
                "options": "Purchase Invoice",
                "width": 120
                },
                {
                "label": "Company Address",
                "fieldname": "billing_address",
                "fieldtype": "Link",
                "options": "Purchase Invoice",
                "width": 120
                },
                {
                "label": "Supplier",
                "fieldname": "supplier",
                "fieldtype": "Link",
                "options": "Supplier",
                "width": 120
                },
                {
                "label": "Supplier Name.",
                "fieldname": "supplier_name",
                "fieldtype": "Data",
                "width": 120
                },
                {
                "label": "Supplier Invoice Date",
                "fieldname": "bill_date",
                "fieldtype": "Data",
                "width": 120
                },
                {
                "label": "Age(Days)",
                "fieldname": "gap_days",
                "fieldtype": "Int",
                "width": 100
                },
                {
                "label": "Expense Gl Account",
                "fieldname": "expense_account",
                "fieldtype": "Link",
                "options":"Account",
                "width": 120
                },
                {
                "label": "Total",
                "fieldname": "base_total",
                "fieldtype": "Data",
                "width": 120
                },
                 {
                "label": "Account Name",
                "fieldname": "account_head",
                "fieldtype": "Data",
                "width": 120
                },
                 {
                "label": " CGST Account Name",
                "fieldname": "cgst_account_head",
                "fieldtype": "Data",
                "width": 120
                },
                 {
                "label": " SGST Account Name",
                "fieldname": "sgst_account_head",
                "fieldtype": "Data",
                "width": 120
                },
                 {
                "label": " IGST Account Name",
                "fieldname": "igst_account_head",
                "fieldtype": "Data",
                "width": 120
                },
                {
                "label": "CGST AMT",
                "fieldname": "cgst",
                "fieldtype": "Float",
                "width": 120
                },
                {
                "label": "SGST AMT",
                "fieldname": "sgst",
                "fieldtype": "Float",
                "width": 120
                },
                {
                "label": "IGST AMT",
                "fieldname": "igst",
                "fieldtype": "Data",
                "width": 120
                },
                {
                 "label": "Reversal Percentage",
                "fieldname": "reversal_percentage",
                "fieldtype": "Data",
                "width": 120
                },
                {
                "label": "Reversal CGST Amt",
                "fieldname": "rcgst",
                "fieldtype": "Data",
                "width": 120
                },
                {
                "label": "Reversal SGST Amt",
                "fieldname": "rsgst",
                "fieldtype": "Data",
                "width": 120
                },
                {
                "label": "Reversal IGST Amt",
                "fieldname": "rigst",
                "fieldtype": "Data",
                "width": 120
                },
                 {
                "label": "State",
                "fieldname": "state",
                "fieldtype": "Link",
                "options":"State",
                "width": 120
                },
]
    data = frappe.db.sql(f"""
SELECT
    pi.`name`,
    pi.`status`,                    
    pi.`posting_date`,
    pi.`billing_address`,
    pi.`supplier`,
    pi.`supplier_name`,
    pi.`bill_date` AS bill_date,
    pii.`expense_account`,
    pi.`base_total`,
    ptc.`account_head` AS account_head ,
    cgst.account_head AS cgst_account_head,
    sgst.account_head AS sgst_account_head,
    igst.account_head AS igst_account_head,
    cgst.tax_amount AS cgst,
    sgst.tax_amount AS sgst,
    igst.tax_amount AS igst
    {select_fields} ,
    cgst.tax_amount * COALESCE({filters.reversal_percentage} , pi.reversal_percentage) /100 AS rcgst,
    sgst.tax_amount * COALESCE({filters.reversal_percentage}   , pi.reversal_percentage)/100 AS rsgst,
    igst.tax_amount * COALESCE({filters.reversal_percentage} , pi.reversal_percentage)/100 AS rigst,
    pi.state
   
FROM
    `tabPurchase Invoice` AS pi
    LEFT JOIN `tabPurchase Invoice Item` AS pii ON pii.parent = pi.name
    LEFT JOIN `tabPurchase Taxes and Charges` AS ptc ON ptc.parent = pi.name
    LEFT JOIN `tabPurchase Taxes and Charges` AS cgst ON cgst.parent = pi.name AND cgst.account_head LIKE '%%CGST%%'
    LEFT JOIN `tabPurchase Taxes and Charges` AS sgst ON sgst.parent = pi.name AND sgst.account_head LIKE '%%SGST%%'
    LEFT JOIN `tabPurchase Taxes and Charges` AS igst ON igst.parent = pi.name AND igst.account_head LIKE '%%IGST%%'
WHERE
    (cgst.account_head LIKE '%%CGST%%' OR sgst.account_head LIKE '%%SGST%%' OR igst.account_head LIKE '%%IGST%%')
    AND pi.docstatus = 1 
    {conditions}
      
GROUP BY
    pi.`name`
ORDER BY
    pi.`name`
 """, as_dict=True)
    for item in data:
        invoice_date = item.get("bill_date")
        if invoice_date:
            present_date = datetime.datetime.now().date()
            gap_days = (present_date - invoice_date).days
            item["gap_days"] = gap_days
    return columns, data
@frappe.whitelist()
def get_data():
    data = frappe.db.sql(f"""
SELECT
    pi.`name`,
    pi.`status`,
    pi.`posting_date`,
    pi.`billing_address`,
    pi.`supplier`,
    pi.`supplier_name`,
    pi.bill_date AS bill_date,
    pii.`expense_account`,
    pi.`base_total`,
    ptc.`account_head` AS account_head ,
    cgst.account_head AS cgst_account_head,
    sgst.account_head AS sgst_account_head,
    igst.account_head AS igst_account_head,
    cgst.tax_amount AS cgst,
    sgst.tax_amount AS sgst,
    igst.tax_amount AS igst,
    50 AS reversal_percentage,
    cgst.tax_amount/2 AS rcgst ,
    sgst.tax_amount/2 AS rsgst ,
    igst.tax_amount/2 AS rigst,
    pi.state

  
FROM
    `tabPurchase Invoice` AS pi
   LEFT JOIN `tabPurchase Invoice Item` AS pii ON pii.parent = pi.name
    LEFT JOIN `tabPurchase Taxes and Charges` AS ptc ON ptc.parent = pi.name
    LEFT JOIN `tabPurchase Taxes and Charges` AS cgst ON cgst.parent = pi.name AND cgst.account_head LIKE '%%CGST%%'
    LEFT JOIN `tabPurchase Taxes and Charges` AS sgst ON sgst.parent = pi.name AND sgst.account_head LIKE '%%SGST%%'
    LEFT JOIN `tabPurchase Taxes and Charges` AS igst ON igst.parent = pi.name AND igst.account_head LIKE '%%IGST%%'
WHERE
    (ptc.account_head LIKE '%%CGST%%' OR ptc.account_head LIKE '%%SGST%%' OR ptc.account_head LIKE '%%IGST%%')
    AND pi.docstatus = 1
GROUP BY
    pi.`name`
ORDER BY
    pi.`name`
""",
as_dict=1)
    for item in data:
        invoice_date = item.get("bill_date")
        if invoice_date:
            present_date = datetime.datetime.now().date()
            gap_days = (present_date - invoice_date).days
            item["gap_days"] = gap_days
    return  data
def get_conditions(filters):
    conditions = ""
    if filters.company:
        conditions +=f' AND pi.company ="{filters.get("company")}" '
    if filters.status:
        conditions +=f' AND pi.status ="{filters.get("status")}" '
    if filters.supplier:
        conditions += f' AND pi.supplier = "{filters.get("supplier")}"'
    if filters.posting_date:
        conditions += f' AND pi.posting_date = "{filters.get("posting_date")}"'

    if filters.reversal_percentage:
        select_fields = f", {filters.reversal_percentage} AS `reversal_percentage`"
    else:
        select_fields = ", pi.reversal_percentage AS `reversal_percentage`"
    if filters.present_date:
        conditions += f' AND pi.posting_date = "{filters.get("posting_date")}"'
    print(select_fields)
    return conditions,select_fields