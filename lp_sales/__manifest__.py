# -*- coding: utf-8 -*-
{
    'name': "lp_sales",

    'summary': """""",

    'description': """
    """,

    'author': "Leading Point",
    'website': "https://leading-point.com",

    'category': 'Leading Point',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sale_crm', 'lp_project', 'lp_crm', 'lp_accounting', 'lp_hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_project_wizard.xml',
        'views/lp_sale_order_view.xml',
    ],
}
