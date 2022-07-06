from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError

class LP_Crm(models.Model):
  _inherit = 'crm.lead'
  lp_company_id = fields.Many2one('res.partner', 'company' , compute = '_compute_company')
  lp_individual_id = fields.Many2many('res.partner')
  lp_OneDrive_url = fields.Char('OneDrive folder URL')
  lp_client_size = fields.Char('Size of the client')
  lp_industry = fields.Selection([('Automobiles_and_Components', 'Automobiles and Components'),
                                  ('banks', 'Banks'),
                                  ('Capital_Goods', 'Capital Goods'),
                                  ('Commercial_Professional_Services', 'Commercial and Professional Services'),
                                  ('Consumer_Durables_Apparel', 'Consumer Durables and Apparel'),
                                  ('Consumer_Services', 'Consumer Services'),
                                  ('Diversified_Financials', 'Diversified Financials'),
                                  ('energy', 'Energy'),
                                  ('Food_Beverage_Tobacco', ' Food, Beverage, and Tobacco'),
                                  ('Food_Staples_Retailing', 'Food and Staples Retailing'),
                                  ('Health_Care_Equipment_Services', ' Health Care Equipment and Services'),
                                  ('Household_Personal_Products', ' Household and Personal Products'),
                                  ('Hospitality', 'Hospitality'),
                                  ('insurance', 'Insurance'),
                                  ('materials', 'Materials'),
                                  ('logistics', 'Logistics'),
                                  ('Media_Entertainment', 'Media and Entertainment'),
                                  ('Pharmaceuticals_Biotechnology_LifeSciences', 'Pharmaceuticals, Biotechnology, and Life Sciences'),
                                  ('Real_Estate', 'Real Estate'),
                                  ('retailing', 'Retailing'),
                                  ('Semiconductors_Semiconductor_Equipment', ' Semiconductors and Semiconductor Equipment'),
                                  ('Software_Services', 'Software and Services'),
                                  ('Technology_Hardware_Equipment', 'Technology Hardware and Equipment'),
                                  ('Telecommunication_Services', 'Telecommunication Services'),
                                  ('transportation', 'Transportation'),
                                  ('travel', 'Travel'),
                                  ('utilities', 'Utilities'),
                                  ('travel', 'Travel'),
                                  ('others', 'Others')
                                  ],
                                 'Indusrty', default="others")
  lp_channel_source = fields.Char('Channel From')
  lp_others = fields.Text('Others Information') #description
  contact_other_info = fields.Text('Others') #description
  lp_opportunity = fields.Selection([('new', 'New'),
                              ('Existing', 'Existing (e.g. CR)'),
                              ('outsourcing_contracts', 'Outsourcing contracts'),
                              ('maintenance', 'Maintenance')],
                             'Opportunity Type', default="new")
  lp_budget = fields.Selection([('yes', 'Yes'),('no', 'No')],'Do they have budget for this opportunity?')
  lp_budget_authority = fields.Selection([('yes', 'Yes'),('no', 'No')],'Authority to use budget ?')
  lp_start_date = fields.Datetime('Start Date')
  lp_end_date = fields.Datetime('Finsh Date')
  lp_department  = fields.Many2one('hr.department','Department',default=lambda self: self.env['hr.department'].search([('lp_category','=','sales_and_marketing')], limit=1))
  lp_go_ahead = fields.Boolean('GoAhead')
  lp_stage_name = fields.Char(related="stage_id.name", string='Stage Name')
  
  created_externally = fields.Boolean("Created Externally")
  mql_score = fields.Char("MQL score")
  autopilot_create_date = fields.Char("Autopilot Create Date")
  lifecycle_stage = fields.Char("Lifecycle Stage")
  persona = fields.Char("Persona")
  request_demo_msg = fields.Char("Request a demo message")

  
  
  
  stage_id = fields.Many2one(
      'crm.stage', string='Stage', index=True, tracking=True,
      compute='_compute_stage_id', readonly=False, store=True,
      copy=False, group_expand='_read_group_stage_ids', ondelete='restrict',
      domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")
  
  def action_new_quotation(self):
    res = super(LP_Crm,self).action_new_quotation()
    res['context']['default_department_id'] = self.lp_department.id
    return res
    
    
  

  @api.model
  def create(self, vals):
     if vals.get("type",False) == "opportunity":
         tmp_project ={
                'name': vals.get('name'),
                'lp_category': 'opportunity',
                'lp_department': vals.get('lp_department'),
         }
    
         project = self.env['project.project'].sudo().create(tmp_project)
         project.message_post(body="Created By: %s"%(self.env.user.partner_id.name))
     return super(LP_Crm, self).create(vals)




  @api.constrains('lp_start_date', 'lp_end_date')
  def check_dates(self):
        if self.lp_start_date and self.lp_end_date:
            if self.lp_start_date > self.lp_end_date:
                raise ValidationError('The date from cannot be greater than date to on Extra Information!')
  @api.depends('partner_id')
  def _compute_company(self):
      self.lp_company_id = self.partner_id



  def notify_dept_head(self):
     marketing_head=self.env['hr.department'].sudo().search([('name','=','Marketing')])
     support_head = self.env['hr.department'].sudo().search([('name', '=', 'Support')])
     if marketing_head and marketing_head.manager_id.user_id.partner_id.id:
      notification_marketing= [(0, 0, {
              'res_partner_id': marketing_head.manager_id.user_id.partner_id.id,
              'notification_type': 'inbox'
          })]
      self.message_post(
              body='Opportunity won:          ' + str(self.name) +'-'
                   +str(self.company_id.name) +'                                        '+'    Dears, ' +'We would like to inform you that the opportunity '
                   +str(self.name)+
                   ' - '
                   +str(self.company_id.name) +
                   ' is won.                regards',              message_type="notification",
              author_id=self.env.user.partner_id.id,
              notification_ids=notification_marketing)
     if support_head and support_head.manager_id.user_id.partner_id.id:
            notification_support= [(0, 0, {
              'res_partner_id': support_head.manager_id.user_id.partner_id.id,
              'notification_type': 'inbox'
             })]
            self.message_post(
              body='Opportunity won:          ' + str(self.name) +'-'
                   +str(self.company_id.name) +'                                        '+'    Dears, ' +'We would like to inform you that the opportunity '
                   +str(self.name)+
                   ' - '
                   +str(self.company_id.name) +
                   ' is won.                regards',              message_type="notification",

              author_id=self.env.user.partner_id.id,
              notification_ids=notification_support)
     if self.lp_department.manager_id.user_id.partner_id.id:
      notification_delivery = [(0, 0, {
              'res_partner_id': self.lp_department.manager_id.user_id.partner_id.id,
              'notification_type': 'inbox'
          })]

      self.message_post(
              body='Opportunity won:          ' + str(self.name) +'-'
                   +str(self.company_id.name) +'                                        '+'    Dears, ' +'We would like to inform you that the opportunity '
                   +str(self.name)+
                   ' - '
                   +str(self.company_id.name) +
                   ' is won.                regards',              message_type="notification",
              author_id=self.env.user.partner_id.id,
              notification_ids=notification_delivery)


  @api.onchange('stage_id')
  def onchange_stage_id(self):
          if self.lp_go_ahead==True:
              self.lp_stage_name = 'Won'

  def write(self, vals):
      qualified = self.env.ref("crm.stage_lead2")
      prospect = self.env.ref("crm.stage_lead1")
      presentation = self.env.ref("lp_crm.stage_lead3")
      new_stage = self.env["crm.stage"].browse(vals.get("stage_id",False))
      sales_department_head = self.env.user.has_group("lp_security.lp_group_sales_dept_head")
      director = self.env.user.has_group("lp_security.director_group")
      if new_stage:
          for rec in self:
              if (new_stage.id == presentation.id or new_stage.sequence > presentation.sequence and rec.stage_id.sequence < presentation.sequence) and not  (sales_department_head or director):
                  raise UserError("You are not allowed to modify the stage.")
      res = super(LP_Crm, self).write(vals)
      for rec in self:
          if rec.stage_id.name=='Won':
           rec.notify_dept_head()

      if vals.get("type",False) == "opportunity":
          for rec in self:
              tmp_project ={
                    'name': rec.name,
                    'lp_category': 'opportunity',
                    'lp_department': vals.get('lp_department',False) or rec.lp_department.id,
             }
        
              project = self.env['project.project'].sudo().create(tmp_project)
              project.message_post(body="Created By: %s"%(self.env.user.partner_id.name))
      return res

class LP_contact(models.Model):
  _inherit = 'res.partner'
  
  created_externally = fields.Boolean("Created Externally")

class LP_stages(models.Model):
  _inherit = 'crm.stage'
