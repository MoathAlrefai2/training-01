import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.osv import expression


class LP_Employee(models.Model):
    _inherit = 'hr.employee'

    lp_employee_history = fields.One2many('employee.history', 'employee_id', string='Employee History')
    lp_is_probation_completed = fields.Boolean('Probation Completed', default=False, groups="hr.group_hr_user")
    lp_is_appraisal_date_due = fields.Boolean('',default=False , compute='is_review_due_date',search='_value_search')
    lp_next_appraisal_date = fields.Date('Review Date' , related='lp_last_appraisal_record.lp_date_to')
    lp_last_appraisal_record = fields.Many2one('hr.appraisal',compute='get_last_appraisal')

    def _value_search(self, operator, value):
        recs = self.search([]).filtered(lambda x: x.lp_is_appraisal_date_due is True)
        if recs:
            return [('id', 'in', [x.id for x in recs])]

    def get_last_appraisal(self):
      for employee in self:
       last_appraisal_record = employee.env['hr.appraisal'].search([('employee_id', '=', employee.id)], limit=1,order='create_date desc')
       if last_appraisal_record:
        employee.lp_last_appraisal_record = last_appraisal_record.id
       else:
           employee.lp_last_appraisal_record = False


    @api.depends('lp_next_appraisal_date')
    def is_review_due_date(self):
     for employee in self:
      if employee.lp_next_appraisal_date:
       if datetime.datetime.now().date() >= employee.lp_next_appraisal_date:
        employee.lp_is_appraisal_date_due = True
       else:
        employee.lp_is_appraisal_date_due = False
      else:
        employee.lp_is_appraisal_date_due = False

 
    