# -*- coding: utf-8 -*-

from odoo import models, fields, api


class lp_timesheet(models.Model):
    _inherit = 'account.analytic.line'

    task_id = fields.Many2one(
        'project.task', 'Task', compute='_compute_task_id', required=True ,store=True, readonly=False, index=True,
        domain="[('company_id', '=', company_id), ('project_id.allow_timesheets', '=', True), ('project_id', '=?', project_id)]")
