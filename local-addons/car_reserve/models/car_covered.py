from odoo import models, fields,api
from odoo.exceptions import UserError
# import tools


class CarCovered(models.Model):
    _name = 'car.covered'
    _description = 'Car Covered'

    name=fields.Char(string="includes name")
    is_free=fields.Boolean("Is Free")
    money_ber_day=fields.Integer("Money Ber Day")