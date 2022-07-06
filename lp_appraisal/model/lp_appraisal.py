from odoo import models, fields, api , _
import logging
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class LP_Appraisal(models.Model):
    _inherit = 'hr.appraisal'

    lp_date_from = fields.Date(string='Date From', tracking=True)
    lp_date_to = fields.Date(string='Date To', tracking=True)
    lp_salary = fields.Float(string='Salary', group_operator=False, tracking=True, groups="hr_appraisal.group_hr_appraisal_manager")
    lp_effective_date = fields.Date(string='Effective Raise Date', tracking=True)
    lp_salary_raise = fields.Float(string='Salary Raise', group_operator=False, tracking=True, groups="hr_appraisal.group_hr_appraisal_manager")
    lp_extra_points = fields.Float(string='Extra Points',  tracking=True, group_operator=False)
    lp_score_perc = fields.Float(string='Score Percentage', compute="_compute_lp_score_perc", tracking=True, group_operator=False, store=True)
    lp_total_score = fields.Float(string='Total Score', compute='_compute_total_score', tracking=True)
    lp_job_id = fields.Many2one('hr.job', string='Current Job Position', tracking=True)
    lp_next_job_id = fields.Many2one('hr.job', string='Next Job Position', tracking=True)
    lp_total_salary = fields.Float(string='Total Salary', compute='_compute_total_salary',  tracking=True, groups="hr_appraisal.group_hr_appraisal_manager")  #
    lp_next_review = fields.Date(string='Next Review Date', tracking=True)
    lp_performance_level = fields.Selection([('elite_plus', 'Elite Plus'),
                                             ('elite', 'Elite'),
                                             ('champion', 'Champion'),
                                             ('warrior', 'Warrior'),
                                             ('soldier', 'Soldier')],
                                            string='Performance Level', compute='_compute_perf_level', tracking=True)
    lp_current_job_level_id = fields.Many2one('x_joblevel', string='Current Job Level', tracking=True)
    lp_next_job_level_id = fields.Many2one('x_joblevel', string='Next Job Level', tracking=True)
    survey_ids = fields.One2many('employee.survey', 'appraisal_id', string='Employee Survey', tracking=True)
    
    
    @api.constrains("lp_date_from","lp_date_to")
    def _constrain_date(self):
        for rec in self.filtered(lambda x:x.lp_date_to and x.lp_date_from and x.lp_date_to < x.lp_date_from):
            raise ValidationError("The ending date must not be prior to the starting date.")
    
    @api.depends("survey_ids","survey_ids.num_of_month","survey_ids.score_percentage")
    def _compute_lp_score_perc(self):
        for rec in self:
            total_score = 0
            for survey in rec.survey_ids:
                total_score += (survey.score_percentage * survey.num_of_month) 
            rec.lp_score_perc = (total_score)/sum(rec.survey_ids.mapped("num_of_month")) if sum(rec.survey_ids.mapped("num_of_month"))  > 0 else 0
    
    @api.model
    def create(self, vals):
        employee = vals.get('employee_id')
        employee_record = self.env['hr.employee'].search([('id', '=', employee)])
        if vals.get('lp_date_to',False):
         date = datetime.datetime.strptime(vals['lp_date_to'],'%Y-%m-%d').date() if type(vals['lp_date_to']) is str else vals['lp_date_to'] 
         if datetime.datetime.now().date() > date:
            employee_record.write({'lp_is_appraisal_date_due': True})
         else:
             employee_record.write({'lp_is_appraisal_date_due': False})
        return super(LP_Appraisal, self).create(vals)


    @api.depends('lp_total_score')
    def _compute_perf_level(self):
        for rec in self:
            if rec.lp_total_score >= 0.0000 and rec.lp_total_score < 0.5000:
                rec.lp_performance_level = 'soldier'
            else:
                rec.lp_performance_level = False
            if rec.lp_total_score >= 0.5000 and rec.lp_total_score < 0.8400:
                rec.lp_performance_level = 'warrior'
            if rec.lp_total_score >= 0.8400 and rec.lp_total_score < 1.1600:
                rec.lp_performance_level = 'champion'
            if rec.lp_total_score >= 1.1600 and rec.lp_total_score < 1.3300:
                rec.lp_performance_level = 'elite'
            if rec.lp_total_score >= 1.3300 and rec.lp_total_score <= 1.5000:
                rec.lp_performance_level = 'elite_plus'
            if rec.lp_total_score > 1.5000:
                rec.lp_performance_level = 'elite_plus'


    @api.onchange('employee_id')
    def set_values_onchange_employee_date(self):
        last_employee_record = self.env['hr.appraisal'].search([('employee_id', '=', self.employee_id.id)], limit=1,
                                                               order='create_date desc')
        if last_employee_record:
            self.lp_date_from = last_employee_record.lp_date_to
            self.lp_date_to = last_employee_record.lp_next_review
        else:
            join_date = self.env['hr.employee'].search([('id', '=', self.employee_id.id)]).x_studio_joining_date
            self.lp_date_from = join_date
            if self.lp_date_from:
                self.lp_date_to = self.lp_date_from + relativedelta(years=+1)
        if self.lp_date_to:
            days = int(datetime.datetime.strptime(str(self.lp_date_to), '%Y-%m-%d').date().day)
            if days == 1:
                self.lp_effective_date = self.lp_date_to
            else:
                days = days - 1
                self.lp_effective_date = self.lp_date_to - relativedelta(days=days)
        else:
            self.lp_effective_date = False
        current_employee_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1,order='create_date desc')
        if current_employee_contract:
         if current_employee_contract.wage:
             self.lp_salary= current_employee_contract.wage

    @api.onchange('employee_id')
    def set_values_onchange_employee_job(self):
        last_appraisal_record = self.env['hr.appraisal'].search([('employee_id', '=', self.employee_id.id)], limit=1,
                                                                order='create_date desc')
        if last_appraisal_record:
            self.lp_current_job_level_id = last_appraisal_record.lp_next_job_level_id.id
            self.lp_job_id = last_appraisal_record.lp_next_job_id.id
        else:
            job_level = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            self.lp_current_job_level_id = job_level.x_studio_job_level.id
            self.lp_job_id = job_level.job_id.id


    @api.depends('lp_salary_raise', 'lp_salary')
    def _compute_total_salary(self):
        self.lp_total_salary = self.lp_salary + self.lp_salary_raise

    @api.onchange('lp_score_perc', 'lp_extra_points')
    def _compute_total_score(self):
        for rec in self:
            rec.lp_total_score = rec.lp_score_perc + rec.lp_extra_points

    def action_confirm(self):
        self.write({'state': 'pending'})

    def action_done(self):

        current_date = datetime.date.today()
        self.write({'state': 'done'})
        for appraisal in self:
            appraisal.employee_id.write({
                'last_appraisal_id': appraisal.id,
                'last_appraisal_date': current_date,
                'next_appraisal_date': False})

    def action_cancel(self):
        self.write({
            'state': 'cancel',
            'date_final_interview': False
        })
        self.mapped('meeting_id').unlink()

    
    
    def send_appraisal(self):
        """
        This function full overwriting is to stop the default behavior of sending email to employee and manager
        and scheduling activity after appraisal confirmation.
        """
        return True
    
    
    @api.onchange('employee_id')
    def set_values_onchange_employee(self):
        if not self.id.origin and self.employee_id.id:
            last_employee_record = self.env['hr.appraisal'].search([('employee_id', '=', self.employee_id.id)], limit=1,
                                                                   order='create_date desc')
            if last_employee_record.lp_total_salary:
                self.lp_salary = last_employee_record.lp_total_salary
            else:
                self.lp_salary = last_employee_record.lp_salary

            if last_employee_record.lp_date_to:
                self.lp_date_from = last_employee_record.lp_date_to
            self.lp_job_id = last_employee_record.lp_next_job_id


class LP_Hrjob(models.Model):
    _inherit = 'hr.job'
    surveys_ids = fields.Many2many('survey.survey', 'survey_id', string='Review Survey')


class EmployeeSurvey(models.Model):
    _name = 'employee.survey'
    _description = 'employee_survey'

    appraisal_id = fields.Many2one('hr.appraisal', string='Appraisal')
    employee_manager_id = fields.Many2one('hr.employee', string='Manager')
    
    
    survey_id = fields.Many2one('survey.survey', string="Survey")
    
    num_of_month = fields.Integer(string='No. Of Month')
    
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    score_percentage = fields.Float(string='Score Percentage', compute="_compute_score_percentage", store=True)
    lp_answer_id = fields.Many2one("survey.user_input", string="Answer")
    lp_answer_state = fields.Selection(related="lp_answer_id.state", string="Status")
    lp_survey_state = fields.Selection(related="survey_id.state")
    performance_levels = fields.Selection([('elite_plus', 'Elite Plus'),
                                           ('elite', 'Elite'),
                                           ('champion', 'Champion'),
                                           ('warrior', 'Warrior'),
                                           ('soldier', 'Soldier')], string='Performance Level',
                                          compute='_compute_perf_level')
    
    @api.constrains("from_date","to_date")
    def _constrain_date(self):
        for rec in self.filtered(lambda x:x.to_date and x.from_date and x.to_date < x.from_date):
            raise ValidationError("The ending date must not be prior to the starting date for employee survey.")
    
    
    @api.depends("lp_answer_id",'lp_answer_id.scoring_percentage')
    def _compute_score_percentage(self):
        for rec in self:
            rec.score_percentage = (rec.lp_answer_id.scoring_percentage)/100 
    
    
    @api.depends('score_percentage')
    def _compute_perf_level(self):
        for rec in self:
            if rec.score_percentage >= 0.0000 and rec.score_percentage < 0.5000:
                rec.performance_levels = 'soldier'
            else:
                rec.performance_levels = False
            if rec.score_percentage >= 0.5000 and rec.score_percentage < 0.8400:
                rec.performance_levels = 'warrior'
            if rec.score_percentage >= 0.8400 and rec.score_percentage < 1.1600:
                rec.performance_levels = 'champion'
            if rec.score_percentage >= 1.1600 and rec.score_percentage < 1.3300:
                rec.performance_levels = 'elite'
            if rec.score_percentage >= 1.3300 and rec.score_percentage <= 1.5000:
                rec.performance_levels = 'elite_plus'
            if rec.score_percentage > 1.5000 or rec.score_percentage < 0 :
                raise UserError('Score Percentage must be between 0 and 1.5!')
    
    def _is_survey_authorized_user(self):
        return self.employee_manager_id.user_id != self.env.user
    
    def start_survey(self):
        self = self.sudo()
        if self._is_survey_authorized_user():
            raise UserError("You are not the assigned manager for this survey.")
        user = self.appraisal_id.employee_id.user_id
        answer = self.survey_id._create_answer(partner=user.partner_id,user=user,check_attempts=False)
        answer.lp_employee_survey_id = self.id
        self.lp_answer_id = answer.id
        action_to_start = self.survey_id.action_start_survey(answer)
        action_to_start["target"] = 'new'
        return action_to_start
    
    def continue_survey(self):
        self = self.sudo()
        if self._is_survey_authorized_user():
            raise UserError("You are not the assigned manager for this survey.")
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/survey/%s/%s' % (self.survey_id.access_token, self.lp_answer_id.access_token)
        }
        
    
    def show_review_result(self):
        action = self.env["ir.actions.actions"]._for_xml_id("survey.action_survey_user_input")

        answer = self.lp_answer_id
        form_view = [(self.env.ref('survey.survey_user_input_view_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = answer.id
        return action 

