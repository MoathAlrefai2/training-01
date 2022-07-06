from odoo import models, fields, api

class LP_JOB_POSITION(models.Model):
    _inherit = "hr.job"
    
        
    lp_job_description_ids = fields.One2many("survey.question", 'lp_job_id', string="Job Description")
    
