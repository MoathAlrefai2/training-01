from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class LP_Contact(models.Model):
  _inherit = 'res.partner'
  lp_label_name = fields.Char('label for name.', default='ind_',readonly=True)
  lp_name = fields.Char('name label',compute='onchange_name')

  lp_attributes = fields.Many2many('hr.job',domain=lambda self:[('id','in',self.execute_domain())])
  def execute_domain(self):
   attributes_names =['Technical','Decision maker','Business influencer','Technical influencer','Information Provider']
   id_list=[]
   for name in attributes_names:
      j=self.env['hr.job'].with_context(lang='en_US').search([('name', '=', str(name))]).id
      id_list.append(j)
   return id_list

  @api.depends('lp_name')
  def onchange_name(self):
      prefix = "ind_"
      if self.company_type == 'person':
       self.lp_name = prefix + self.name
      else:
        self.lp_name = self.name
