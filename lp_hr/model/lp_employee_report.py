from odoo import models, fields, api

class LP_Contract_employee(models.Model):
    _inherit = 'hr.contract.employee.report'

    lp_contract_status = fields.Selection(related="contract_id.state", string='Contract state')