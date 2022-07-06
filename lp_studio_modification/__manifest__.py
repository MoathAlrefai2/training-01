# -*- coding: utf-8 -*-
{
    'name': "lp_studio_modification",

    'summary': """""",

    'description': """
    this module to edit on fields that's created via odoo studio on leading point database only .
    """,

    'author': "Leading Point",
    'website': "https://leading-point.com",

    'category': 'Leading Point',
    'version': '14.0.1',

    'depends': ['base'],
    'installable': True,
    'auto_install': True,
    'post_init_hook': 'delete_selection_field_values',
    'data': [
    ],
}
