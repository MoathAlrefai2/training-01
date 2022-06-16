from odoo import models, fields,api
# import tools


class history(models.Model):
    _name = 'car.history'
    _description = 'Car History'

    user= fields.Many2one('res.users', string='User')
    id_user=fields.Integer('Id User')
    name=fields.Char("Name")
    reserved_from=fields.Date("Reserved From")
    reserved_to = fields.Date("Reserved To")
    num_of_day=fields.Integer(string="Num Of Day")
    price=fields.Integer("Price")


    @api.onchange('reserved_to')
    def onchange_member(self):
        for user in self:
            if user.reserved_to:
                self.num_of_day = (self.reserved_to - self.reserved_from).days



