{
    'name': 'LP Base import Inherit',
    'description': """Modify import module to make it receive a excel files with different templates that odoo accept""",
    'depends': ['base_import','hr','lp_crm'],
    'category': 'Leading Point',
    'author': "Leading Point",
    'website': "https://leading-point.com",
    'version': '14.0.0',
    'installable': True,
    'data': ['views/lp_base_import_templates.xml',
    'security/ir.model.access.csv'
    ],
    'qweb': ['static/src/xml/base_import.xml'],
}
