{
    'name':"lp_appraisal",
    "description":'(lp_appraisal) inherit hr appraisal'  ,
    'summary': """Modifications for apprasial module , https://www.leading-point.com/""",

    'description': """
      Modifications for appraisal
  """,

    'author': "Leading Point",
    'website': "https://www.leading-point.com",
 'data': [
     'security/ir.model.access.csv',
     'views/lp_assets.xml',
     'views/survey_template.xml',
     'views/lp_job_position.xml',
     'views/lp_survey.xml',
'views/lp_appraisal.xml',
'security/security.xml',
'views/lp_appraisal_survey.xml'
    ],
    'version':'5.2',
     'category': 'Leading Point',
    'depends':
        ['hr','survey','base','hr_appraisal']

}
