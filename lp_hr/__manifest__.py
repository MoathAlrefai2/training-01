{
    'name':"lp_hr",
    "description":'(lp_hr) inherit from (hr)',
    'summary': """
      Modifications for employee module , https://leading-point.com/""",

    'description': """
      Modifications for hr 
  """,
    'version':'14.0.1.1',
    'author': "Leading Point",
    'website': "https://leading-point.com",
 'data': [
     'security/groups.xml',
     'security/ir.model.access.csv',
     'views/lp_asset_type.xml',
     'views/lp_asset_management.xml',
'views/lp_employee.xml',
'views/lp_employee_history.xml',
'views/lp_department.xml',
'views/lp_employee_report_filter.xml'
    ],
'post_init_hook': 'set_probation_completed_field_true',
     'category': 'Leading Point',
    'depends':[
        'base','hr','hr_contract_reports','lp_appraisal','account_asset','hr_attendance'
    ]
}