odoo.define('lp_appraisal.survey.form', function(require) {
	'use strict';
	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var _t = core._t;
	var survey = require("survey.form")
	survey.include({
		_validateForm:  function($form, formData) {
			var res = this._super($form, formData)
			var errors = {};
			$form.find('[data-question-type]').each(function() {
				var $input = $(this);
				var $questionWrapper = $input.closest(".js_question-wrapper");
				var questionId = $questionWrapper.attr('id');
				switch ($input.data('questionType')) {
					case 'simple_choice_radio':
					case 'multiple_choice':
						var answer = $(this).closest('.o_survey_form_choice').find('label.o_survey_selected').data('score')
						var $textarea = $questionWrapper.find('textarea').val();
						if (answer && $textarea != undefined && $textarea.trim() == '' && parseInt(answer) != 100) {
							errors[questionId] = "Specify Your Notes!"
						}
				}
			});
			if (_.keys(errors).length > 0) {
				this._showErrors(errors);
				return false;
			}
			return res;
		}

	})
})