# -*- coding: utf-8 -*-
{
    "name": "Account Invoice Fixed Discount",
    "summary": "Allows to apply fixed amount discounts on invoice lines.",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Samrawi B, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_move_view.xml",
        "views/report_invoice.xml",
    ],
}
