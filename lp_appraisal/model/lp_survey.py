from odoo import models, fields, api
from odoo.exceptions import UserError , ValidationError
 
class LP_SURVEY_QuestionAnswer(models.Model):
    _inherit = "survey.question.answer"
    
    lp_suggested_answer_company_id = fields.Many2one("appraisal.survey.template", copy=False) 

class LP_SURVEY_USERINPUT(models.Model):
    _name = "survey.user_input"
    _inherit = ["survey.user_input",'mail.thread', 'mail.activity.mixin']
    
    scoring_percentage = fields.Float(tracking=True)
    lp_employee_survey_id = fields.Many2one("employee.survey")
    lp_performance_leve = fields.Selection(related="lp_employee_survey_id.performance_levels", string="Performance Level")
    
    def write(self,vals):
        if any(rec.lp_employee_survey_id and rec.lp_employee_survey_id.appraisal_id.state == 'done' for rec in self):
            raise UserError("You can't update the review for done appraisals.")
        
        return super(LP_SURVEY_USERINPUT, self).write(vals)
        
    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id', 'predefined_question_ids.answer_score')
    def _compute_scoring_values(self):
        res = super(LP_SURVEY_USERINPUT, self)._compute_scoring_values()
        for user_input in self.filtered(lambda x:x.lp_employee_survey_id):
            answers_per_section = {}
            score_percentage = 0
            for line in user_input.user_input_line_ids:
                if answers_per_section.get(line.page_id):
                    answers_per_section[line.page_id]['answers'] += line
                else:
                    answers_per_section[line.page_id] = {}
                    answers_per_section[line.page_id]["answers"] = line
            for section in answers_per_section:
                section_performance = sum(answers_per_section[section]["answers"].mapped("answer_score")) / len(answers_per_section[section]["answers"])
                answers_per_section[section]["section_performance"] = section_performance 
                score_percentage += (section_performance * section.lp_weight/100)
                
            user_input.scoring_percentage = score_percentage
     
    def is_simple_choice_with_comment(self,question,answers,comment):
        return answers and comment and  question.comments_allowed and not question.comment_count_as_answer \
                and question.question_type == "simple_choice"
           
    def _save_line_choice(self, question, old_answers, answers, comment):
        if self.is_simple_choice_with_comment(question,answers,comment):
            
            if not (isinstance(answers, list)):
                answers = [answers]
            vals_list = []
            for answer in answers:
                val = self._get_line_answer_values(question, answer, 'suggestion')
                val["lp_reviewer_note"] = comment
                vals_list.append(val)
            old_answers.sudo().unlink()
            return self.env['survey.user_input.line'].create(vals_list)
        return  super(LP_SURVEY_USERINPUT, self)._save_line_choice(question, old_answers, answers, comment)
    
class LP_SURVEY_USERINPUT_LINE(models.Model):
    _inherit = "survey.user_input.line"
    
    lp_reviewer_note = fields.Text("Reviewer Note")
    lp_question_type = fields.Selection(related="question_id.question_type")
    lp_question_suggested_answer_ids = fields.One2many(related="question_id.suggested_answer_ids")
    lp_appraisal_survey = fields.Boolean(related="question_id.survey_id.lp_available_on_appraisal")
    
    @api.onchange("suggested_answer_id")
    def _onchange_suggested_answer_id(self):
        self.answer_score = self.suggested_answer_id.answer_score

class LP_SURVEY_QUESTION(models.Model):
    _inherit = "survey.question"
    
    lp_job_id = fields.Many2one("hr.job", copy=False)
    lp_behavioral_company_id = fields.Many2one("appraisal.survey.template", copy=False)
    lp_previous_goals_compny_id = fields.Many2one("appraisal.survey.template", copy=False)
    lp_feedback_compny_id = fields.Many2one("appraisal.survey.template", copy=False)
    lp_weight = fields.Float("Weight%")
    comments_message = fields.Char(default="Reviewer Note")
    
    
    def _is_appraisal_simple_question(self):
        return self._context.get("appraisal_question",False) and self.question_type == "simple_choice"
    
    def _get_suggestions_vals(self):
        field = self._context.get('field',False)
        if field == 'lp_job_id' or not field:
            template = self.env["appraisal.survey.template"].search([],limit=1,order="id desc")
        elif field:
            template = getattr(self, field)
            
        return template.lp_possible_suggested_answer_ids
    
        
    @api.onchange("question_type")
    def _onchange_question_type(self):
        if self._is_appraisal_simple_question():
            self.comments_allowed = True
            suggested_answers = self._get_suggestions_vals()
            for answer in suggested_answers:
                copied_answer = answer.copy({'question_id':self.id})
        else:
            self.suggested_answer_ids = False
    
class LP_SURVEY(models.Model):
    _inherit = "survey.survey"
    
    lp_available_on_appraisal = fields.Boolean("Available on Appraisal")
    lp_job_id = fields.Many2one("hr.job", string="Job Position")
    
    @api.onchange("lp_available_on_appraisal")
    def _onchange_lp_available_on_appraisal(self):
        if not self.lp_available_on_appraisal:
            self.question_and_page_ids.unlink()
            self.lp_job_id = False
    
    def _generate_pc_questions(self,seq,template):
        bc_questions = template.lp_behavioral_competencies_question_ids
        bc_page = self.env['survey.question'].create({'sequence':seq,'lp_weight':template.lp_behavioral_competencies_weight,'title':'Behavioral Competencies','is_page':True})
        
        self.question_and_page_ids = [(4,bc_page.id)]
        for question in bc_questions:
            seq+=1
            copied_question = question.copy({'sequence':seq,'page_id':bc_page.id})
            if copied_question:
                self.question_and_page_ids = [(4,copied_question.id)]
        return seq
        
    def _generate_pg_questions(self,seq,template):
        pg_questions =  template.lp_previous_goals_question_ids 
        pg_page = self.env['survey.question'].create({'sequence':seq,'lp_weight':template.lp_previous_goals_weight,'title':'Previous Goals','is_page':True})
        self.question_and_page_ids = [(4,pg_page.id)]
        for question in pg_questions:
            seq+=1
            copied_question = question.copy({'sequence':seq,'page_id':pg_page.id})
            if copied_question:
                self.question_and_page_ids = [(4,copied_question.id)] 
        return seq 
    
    def _generate_fb_questions(self,seq,template):
        fb_question = template.lp_feedback_question_ids
        fb_page = self.env['survey.question'].create({'sequence':seq,'lp_weight':0,'title':'Feedback','is_page':True})
        self.question_and_page_ids = [(4,fb_page.id)]
        for question in fb_question:
            seq+=1
            copied_question = question.copy({'sequence':seq,'page_id':fb_page.id})
            if copied_question:
                self.question_and_page_ids = [(4,copied_question.id)]
        return seq
    
    
    def _get_company_appraisal_questions(self):
        template = self.env['appraisal.survey.template'].search([],limit=1,order="id desc")
        if self.lp_available_on_appraisal:
            self.scoring_type = 'scoring_with_answers'
            company = self.env.company
            seq = self._generate_pc_questions(100,template)
            seq = self._generate_pg_questions(seq+1,template)
            seq = self._generate_fb_questions(seq+1,template)
        
    
    @api.onchange("lp_job_id")
    def _onchange_job_id(self):
        self.question_and_page_ids = False
        template = self.env['appraisal.survey.template'].search([],limit=1,order="id desc")
        if self.lp_job_id:
            self._get_company_appraisal_questions()
            questions = self.lp_job_id.lp_job_description_ids
            seq = 0
            job_position_page = self.env['survey.question'].create({'sequence':seq,'lp_weight':100 - (template.lp_behavioral_competencies_weight + template.lp_previous_goals_weight)
                                                                    ,'title':' Job Description','is_page':True})
            self.question_and_page_ids = [(4,job_position_page.id)]
            for question in questions:
                seq +=1
                copied_question = question.copy({'sequence':seq,'page_id':job_position_page.id})
                if copied_question:
                    self.question_and_page_ids = self.question_and_page_ids + copied_question
                
    