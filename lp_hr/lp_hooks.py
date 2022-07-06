from odoo import api, fields, SUPERUSER_ID

def set_probation_completed_field_true(cr, registry):

  env = api.Environment(cr, SUPERUSER_ID, {})
  cr.execute('update hr_employee set lp_is_probation_completed=True')
