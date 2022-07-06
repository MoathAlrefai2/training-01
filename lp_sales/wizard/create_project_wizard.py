# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class CreateProjectWizard(models.TransientModel):
    _name = "create.project.wizard"

    name = fields.Char('Name')
    department_id = fields.Many2one('hr.department', 'Department')
    allow_timesheets = fields.Boolean('Timesheet')
    allow_billable = fields.Boolean('Billable')
    
    def create_project(self):
        vals = {
            'name' : self.name,
            'lp_department' : self.department_id.id,
            'allow_timesheets' : self.allow_timesheets,
            'allow_billable' : self.allow_billable
            }
        project_id = self.env['project.project'].create(vals)
        sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
        sale_order.lp_project_id = project_id.id