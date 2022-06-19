{
    'name': "Car Reserve",
    'summary': "Reserve Cars Easily",
    'description': """
Manage Cars
==============
Description related to Store.
""",
'license': 'GPL-3',
    'author': "Ahmad",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '14.0.1',
    'depends': ['base', 'website'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',

        'views/templates2.xml',
        'views/car_reserve.xml',
        'views/user.xml',
        'views/car_type.xml',
        'views/car_covered.xml',

        # 'views/snippets.xml',

    ],
    'demo': [],
    'assets': {
        'web.assets_frontend': [
            "/car_reserve/static/src/css/popup.css",
            "/car_reserve/static/src/css/ui.css",
            "/car_reserve/static/src/js/popup.js",
        ],
        'web.assets_backend': [
            "/car_reserve/static/src/css/style.css",

        ],
    },

}
