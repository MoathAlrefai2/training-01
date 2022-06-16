from odoo import models, fields,api
# import tools


class User(models.Model):
    _inherit = 'res.users'
    whish_list = fields.Many2one('car.whishlist',string="reserved list")





