{
    'name':"lp_contact",
    "description":'(lp_contact) inherit from (res.partner)',
    'summary': """
      Modifications for contact module , https://leading-point.com/""",

    'description': """
      Modifications for contact
  """,

    'author': "Leading Point",
    'website': "https://leading-point.com",
 'data': [
'views/lp_contact.xml',
'data/positions.xml'
    ],
     'category': 'Leading Point',
    'depends':[
        'base','contacts','hr'
    ]
}
