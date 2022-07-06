# -*- coding: utf-8 -*-
{
    'name': "lp_accounting",

    'summary': """""",

    'description': """
    """,

    'author': "Leading Point",
    'website': "https://leading-point.com",

    'category': 'Leading Point',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant','analytic'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/lp_account_move_views.xml',
        'views/lp_analytic_account_group.xml',

    ],
}
