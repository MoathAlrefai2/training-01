from odoo import models, fields, api , _
from odoo.exceptions import UserError


class Lp_Appraisal_Survey(models.Model):
    _name = 'appraisal.survey.template'
    _rec_name = "lp_name"
    _description = 'Appraisal Survey Template'
    
    lp_name = fields.Char("Name")
    lp_behavioral_competencies_question_ids = fields.One2many("survey.question", 'lp_behavioral_company_id', copy=False,
                                                               string="Behavioral Competencies")
    lp_previous_goals_question_ids = fields.One2many("survey.question", 'lp_previous_goals_compny_id', copy=False, string="Previous Goals")
    lp_feedback_question_ids = fields.One2many("survey.question", 'lp_feedback_compny_id', copy=False, string="Feedback")
    lp_behavioral_competencies_weight = fields.Float("Behavioral Competencies Weight", help="This field value will be considered as a weight for questions under this section scoring")
    lp_previous_goals_weight = fields.Float("Previous Goals Weight", help="This field value will be considered as a weight for questions under this section scoring" )
    lp_possible_suggested_answer_ids = fields.One2many("survey.question.answer","lp_suggested_answer_company_id", string="Possible Suggested Answers")
    
    
    