# -*- coding: utf-8 -*-

from odoo import models, fields, api
class SaleAdvancePaymentInvInh(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super(SaleAdvancePaymentInvInh, self)._prepare_invoice_values(order, name, amount, so_line)
        if not order.flag_order_lines:
            analytic_account_id = order.department_id.lp_analytic_account_group.lp_analytic_account
        else:
            analytic_account_id = order.lp_project_id.analytic_account_id or False
        res['invoice_line_ids'][0][2]['analytic_account_id'] = analytic_account_id

        analytic_account_group_id = order.department_id.lp_analytic_account_group
        res['invoice_line_ids'][0][2]['analytic_account_group_id'] = analytic_account_group_id
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        if not self.order_id.flag_order_lines:
            analytic_account_id = self.order_id.department_id.lp_analytic_account_group.lp_analytic_account
        else:            
            analytic_account_id = self.order_id.lp_project_id.analytic_account_id or False
        
        res = super(SaleOrderLine,self)._prepare_invoice_line(**optional_values)
        res['analytic_account_id'] = analytic_account_id
        res['analytic_account_group_id'] = self.order_id.department_id.lp_analytic_account_group
        return res

class LpSales(models.Model):
    _inherit = 'sale.order'

    department_id = fields.Many2one('hr.department', string="Department")
    flag_order_lines = fields.Boolean(compute = '_compute_flag_order_lines')
    lp_project_id = fields.Many2one('project.project', string="Project")

    @api.onchange('order_line')
    def reseller_flag_order_lines(self):
        flag = False
        for record in self.order_line:
            if not record.product_id.lp_resalable and not record.is_downpayment:
                flag = True
        
        self.flag_order_lines = flag 
    
    @api.depends('order_line')
    def _compute_flag_order_lines(self):
        flag = False
        for record in self.order_line:
            if not record.product_id.lp_resalable and not record.is_downpayment:
                flag = True
        
        self.flag_order_lines = flag

    @api.onchange('department_id')
    def get_analytic_account(self):
        analytic_account = self.department_id.lp_analytic_account_group.lp_analytic_account.id
        if analytic_account:
            self.analytic_account_id = analytic_account

    def action_open_project(self):
        return {
            'name': 'Project',
            'view_mode': 'form',
            'views': [(False,'form')],
            'res_model': 'project.project',
            'res_id': self.lp_project_id.id,
            'type': 'ir.actions.act_window',
            'traget':'current'
        }