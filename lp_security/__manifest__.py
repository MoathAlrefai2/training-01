{
    'name':"lp_security",
    'summary': """
      Modifications for access rights for menu items , https://leading-point.com/""",

    'description': """
      Modifications for menus access rights 
  """,
    'version':'14.0.1.1',
    'author': "Leading Point",
    'website': "https://leading-point.com",
 'data': [
  'security/lp_groups.xml',
 'security/ir.model.access.csv',
'views/menus.xml',
'views/views.xml',
'security/record_rules.xml',
'security/model_access.xml',
    ],
     'category': 'Leading Point',
    'depends':[
        'base','hr','sale_timesheet','mail','contacts','calendar','hr_holidays','hr_appraisal',
        'hr_expense','website','utm','lp_project','lp_hr','hr_gamification','lp_appraisal','lp_crm'
    ]
}
