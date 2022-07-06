{
    'name':"lp_crm",
    "description":'(lp_crm) inherit from (crm.lead)',
    'summary': """
      Modifications for contact module , https://leading-point.com/""",
    'description': """
      Modifications for CRM
  """,

    'author': "Leading Point",
    'website': "https://leading-point.com",
    'data': [
        'security/lp_groups.xml',
        'security/ir.model.access.csv',
        'data/stages_data.xml',
        'data/automated_action.xml',
        'data/lp_category.xml',
        'views/lp_crm.xml',
        'views/lp_product.xml',
    ],
    'version': '14.0.2',
     'category': 'Leading Point',
    'depends': ['base','crm','contacts','mail','base_automation','sale','sale_crm','lp_hr','auth_api_key']
}
