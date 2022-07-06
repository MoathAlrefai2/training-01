# -*- coding: utf-8 -*-

from odoo import models, fields, api


class lp_accounting(models.Model):
    _inherit = 'account.move.line'

    analytic_account_group_id = fields.Many2one('account.analytic.group', string='Analytical Account Group')

    @api.onchange('analytic_account_group_id')
    def _onchange_analytic_account_group_id(self):
        self.analytic_account_id = False
        if self.analytic_account_group_id:
            return {'domain': {'analytic_account_id' : [('group_id', '=', self.analytic_account_group_id.id)]}}
