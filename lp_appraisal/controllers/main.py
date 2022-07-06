# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.survey.controllers.main import Survey

class CustomSurvey(Survey):
    
    def _check_appraisal_survey_validity(self,survey_token, answer_token):
        survey_sudo, answer_sudo = self._fetch_from_access_token(survey_token, answer_token)
        emp_survey = answer_sudo.lp_employee_survey_id
        is_appraisal_manager = emp_survey and request.env.user == emp_survey.employee_manager_id.user_id
        is_appraisal_employee =  emp_survey.appraisal_id.employee_id.user_id.partner_id == answer_sudo.partner_id
        return  is_appraisal_manager and is_appraisal_employee
        
    def _check_validity(self, survey_token, answer_token, ensure_token=True, check_partner=True):
        result = super(CustomSurvey, self)._check_validity(survey_token, answer_token, ensure_token,check_partner)
        if result == 'answer_wrong_user' and self._check_appraisal_survey_validity(survey_token, answer_token):
            return True
        return result
        


