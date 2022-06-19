from odoo import models, fields,api
from odoo.exceptions import UserError
# import tools


class CarType(models.Model):
    _name = 'car.type'
    _description = 'Car Type'

    name= fields.Char('Name Of Type')
    num_of_passengers = fields.Integer('Passengers', required=True)
    num_of_large_bags = fields.Integer('Large Bags')
    num_of_small_bags = fields.Integer('Small Bags')
    num_of_doors = fields.Integer('Doors')
    img = fields.Binary("Car Image")
