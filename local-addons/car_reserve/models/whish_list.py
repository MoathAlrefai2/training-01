from odoo import models, fields,api
from odoo.exceptions import UserError
# import tools


class CarWhishList(models.Model):
    _name = 'car.whishlist'
    _description = 'Car WhishList'


    cars=fields.Many2many('car.reserve',string="Cars")