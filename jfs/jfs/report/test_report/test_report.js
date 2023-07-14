frappe.query_reports["Test Report"] = {
  filters: [
    {
      fieldname: "company",
      label: "Company",
      fieldtype: "Link",
      options: "Company",
    },
    {
      fieldname: "supplier",
      label: "Supplier",
      fieldtype: "Link",
      options: "Supplier",
    },
    {
      fieldname: "posting_date",
      label: "From Date",
      fieldtype: "Date",
    },
    {
      fieldname: "posting_date",
      label: "To Date",
      fieldtype: "Date",
    },
    {
      fieldname: "reversal_percentage",
      label: "Reversal Percentage",
      fieldtype: "Float",
      "default":50
    },
  ],
  onload: function (report) {
    var newButton = report.page.add_inner_button(
      __("Make Reversal"),
      function () {
        // Custom button functionality here
        frappe.call({
          method: "jfs.jfs.report.test_report.test_report.get_data",
      args: {
      'filters': {
        'company': frappe.query_report.get_filter_value('company'),
        'supplier': frappe.query_report.get_filter_value('supplier'),
        'posting_date': frappe.query_report.get_filter_value('posting_date'),
        'reversal_percentage': frappe.query_report.get_filter_value('reversal_percentage')
      },
    },
          callback: function (r) {
            console.log(r.message);
            if (r.message == "0") {
              frappe.msgprint("No Purchase  found");
            } else {
              dialog.hide();
              create_dialog_employee(r.message);
            }
          },
        });
        // Open a popup dialog
        var dialog = new frappe.ui.Dialog({
          title: __("Make Reversal"),
          primary_action: function () {
            // Perform the reversal action using the entered values
            var reversalPercentage = dialog.get_value("reversal_percentage");
            // Code for reversal action goes here
            // Close the dialog
            dialog.hide();
          },
          primary_action_label: __("Submit"),
        });
        dialog.show();
      }
    );
  },
};
function create_dialog_employee(emp_data) {
  var data = {};
  let d = new frappe.ui.Dialog({
    title: "Reversal Document",
    fields: [
      {
        label: "Purchase Invoice",
        fieldname: "purchase_invoice",
        fieldtype: "Table",
        cannot_add_rows: true,
        in_place_edit: false,
        data: [],
        fields: [
          {
            fieldname: "name",
            columns: 2,
            fieldtype: "Link",
            option: "Purchase Invoice",
            in_list_view: 1,
            label: "Purchase Invoice",
          },
          {
            fieldname: "posting_date",
            columns: 2,
            fieldtype: "Date",
            in_list_view: 1,
            label: "Posting Date",
          },
          {
            fieldname: "bill_date",
            columns: 2,
            fieldtype: "Date",
            in_list_view: 1,
            label: "Supplier Invoice Date",
          },
          {
            fieldname: "gap_days",
            columns: 2,
            fieldtype: "int",
            in_list_view: 1,
            label: "Age(Days)",
          },
          {
            fieldname: "billing_address",
            columns: 2,
            fieldtype: "Link",
            in_list_view: 1,
            label: "Company Address",
          },
          {
            fieldname: "expense_account",
            columns: 2,
            fieldtype: "Link",
            option: "Account",
            in_list_view: 1,
            label: "Expense Account",
          },
          {
            fieldname: "account_head",
            columns: 2,
            fieldtype: "Link",
            in_list_view: 1,
            label: "Account Name",
          },
          {
            fieldname: "cgst_account_head",
            columns: 2,
            fieldtype: "Link",
            option: "Account",
            in_list_view: 1,
            label: "CGST Account Head ",
          },
          {
            fieldname: "sgst_account_head",
            columns: 2,
            fieldtype: "Link",
            in_list_view: 1,
            label: "SGST Account Head",
          },
          {
            fieldname: "cgst",
            columns: 1,
            fieldtype: "Data",
            in_list_view: 1,
            label: "CGST AMT",
          },
          {
            fieldname: "sgst",
            columns: 1,
            fieldtype: "Data",
            in_list_view: 1,
            label: "SGST AMT",
          },
          {
            fieldname: "igst",
            columns: 1,
            fieldtype: "Data",
            in_list_view: 1,
            label: "IGST AMT",
          },
          {
            fieldname: "reversal_percentage",
            columns: 1,
            fieldtype: "Data",
            in_list_view: 1,
            label: "Reversal Percentage",
          },
          {
            fieldname: "rcgst",
            columns: 1,
            fieldtype: "Data",
            in_list_view: 1,
            label: "Reversal CGST Amt",
          },
          {
            fieldname: "rsgst",
            columns: 1,
            fieldtype: "Data",
            in_list_view: 1,
            label: "Reversal SGST Amt",
          },
          {
            fieldname: "rigst",
            columns: 1,
            fieldtype: "Data",
            in_list_view: 1,
            label: "Reversal IGST Amt",
          },
        ],
      },
    ],
    primary_action_label: "Submit",
    primary_action(values) {
      let selected_items = cur_dialog.fields_dict.purchase_invoice.grid.get_selected_children();
    console.log(selected_items.length)
    let date = new Date().toLocaleDateString("de-DE");
    console.log(date)
      if (selected_items.length > 0) {
        let arraya = [];
        for (let item of selected_items) {
          if (item.igst) {
            arraya = [
              {
                account: item.account_head,
                debit_in_account_currency: 0,
                credit_in_account_currency: item.igst,
              },
              {
                account: item.expense_account,
                debit_in_account_currency: item.igst,
                credit_in_account_currency: 0,
              },
            ];
          } else {
            arraya = [
              {
                account: item.cgst_account_head,
                debit_in_account_currency: 0,
                credit_in_account_currency: item.cgst,
              },
              {
                account: item.sgst_account_head,
                debit_in_account_currency: 0,
                credit_in_account_currency: item.sgst,
              },
              {
                account: item.expense_account,
                debit_in_account_currency: item.cgst * 2,
                credit_in_account_currency: 0,
              },
            ];
          }
          frappe.db
            .insert({
              doctype: "Journal Entry",
              posting_date: frappe.datetime.nowdate(),
              voucher_type: "Reversal Of ITC",
              reversal_type: "Others",
              company_address: item.billing_address,
              accounts: arraya,
            })
            .then((doc) => {
              console.log(doc);
            });
        }
      } else {
        frappe.msgprint("Please Select The checkboxes");
      }
      // let data_vls=values['employee_name']
      // data_vls.forEach((i) => {
      //   var a = frappe.model.add_child(cur_frm.doc, "Journal Entry", "accounts");
      //    a.employee = i.employee;
      // })
      // refresh_field("project_employee_allocation");
      d.hide();
    },
  });
  setTimeout(function () {
    $.each(emp_data, function (i, d) {
      cur_dialog.fields_dict.purchase_invoice.df.data.push({
        name: d.name,
        posting_date:d.posting_date,
        bill_date:d.bill_date,
        gap_days:d.gap_days,
        billing_address: d.billing_address,
        account_head: d.account_head,
        expense_account: d.expense_account,
        cgst_account_head: d.cgst_account_head,
        sgst_account_head: d.sgst_account_head,
        cgst: d.cgst,
        sgst: d.sgst,
        igst: d.igst,
        reversal_percentage: d.reversal_percentage,
        rcgst: d.rcgst,
        rsgst: d.rsgst,
        rigst: d.rigst,
      });
      data = cur_dialog.fields_dict.purchase_invoice.df.data;
      cur_dialog.fields_dict.purchase_invoice.grid.refresh();
    });
  }, 1000);
  d.show();
  d.$wrapper.find(".modal-dialog").css("max-width", "60%");
}
