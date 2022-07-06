from odoo import models, fields, api
from odoo.exceptions import UserError

class Lp_Empolyee_History(models.Model):
    _name = 'employee.history'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    lp_previous_company = fields.Char('Previous Company')
    lp_join_date = fields.Date('Joining Date')
    lp_expertised = fields.Char('Expertised In')
    lp_end_date = fields.Date('End Date')
    lp_Reason_left = fields.Char('Reason For Left')
    lp_salary = fields.Integer('Salary')
    lp_experience = fields.Float('Experience (Year/month)',compute='get_duration',digits=(12,1))

    def get_duration(self):
        self.lp_experience = 0
        for each in self:
            if each.lp_end_date and each.lp_join_date:
                duration = fields.Date.from_string(each.lp_end_date) - fields.Date.from_string(each.lp_join_date)
                each.lp_experience = (duration.days + duration.seconds/86400)/365.2425

    @api.constrains('lp_join_date', 'lp_end_date')
    def check_dates(self):
        if self.lp_join_date and self.lp_end_date:
            if self.lp_join_date > self.lp_end_date:
                raise UserError('The date from cannot be greater than date to')
