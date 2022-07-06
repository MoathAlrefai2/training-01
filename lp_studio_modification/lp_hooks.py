from odoo import api, fields, SUPERUSER_ID

def delete_selection_field_values(cr, registry):

  env = api.Environment(cr, SUPERUSER_ID, {})

  cr.execute("delete from ir_model_fields_selection where field_id in (select id from ir_model_fields where name ='x_studio_travel_for' and model = 'x_trip') and ir_model_fields_selection.value != 'Project' ")
  cr.execute("delete from ir_model_fields_selection where field_id in (select id from ir_model_fields where name ='x_studio_working_on' and model = 'x_awardeddays') and ir_model_fields_selection.value != 'Project' ")
  cr.execute("delete from ir_model_fields_selection where field_id in (select id from ir_model_fields where name ='x_studio_expense_for' and model = 'hr.expense') and ir_model_fields_selection.value != 'Project' ")
