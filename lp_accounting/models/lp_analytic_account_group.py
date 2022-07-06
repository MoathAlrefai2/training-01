from odoo import models, fields, api

class LPAccount_group(models.Model):
    _inherit = 'account.analytic.group'

    lp_analytic_account = fields.Many2one('account.analytic.account', string='Default Analytical Account')