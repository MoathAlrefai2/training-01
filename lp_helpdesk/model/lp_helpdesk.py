from odoo import models, fields, api, _

from odoo.osv import expression

class LP_Helpdesk(models.Model):
  _inherit = 'helpdesk.ticket'

  lp_affected_system = fields.Many2many('helpdesk.affected',string="many2many_default" , ondelete="cascade")
  lp_analysis_result = fields.Text('Analysis Result')
  lp_related_item = fields.Char('Related Items')
  lp_previntive_action = fields.Boolean('Requries Previntive Action')
  lp_clousure_reason = fields.Many2one('clousure.reason')
  lp_internal_note = fields.Text('Internal Notes')
  lp_knowledge_base_relvant = fields.Boolean('Knowledge Base Relevant')
  lp_is_billable = fields.Boolean('Is Billable')
  lp_estimated_hours = fields.Float('Estimated Hours')
  lp_actual_hours = fields.Float('Actual Hours')

  lp_level_of_support = fields.Selection(selection=[
      ('l1', 'Level 1'),
      ('l2', 'Level 2'),
      ('l3', 'Level 3')
  ], string='Level of Support', default='l1')

  priority = fields.Selection(selection=[
      ('0', 'All'),
      ('1', 'Low priority'),
      ('2', 'Medium priority'),
      ('3', 'High priority'),
      ('4', 'Urgent'),
  ], string='Priority', default='0')

  def _sla_find(self):

      res = super(LP_Helpdesk, self)._sla_find()

      for sla in res:
          domain = [('team_id', '=', self.team_id.id), ('priority', '=', self.priority),
                        '|',
                            '&', ('stage_id.sequence', '>=', self.stage_id.sequence), ('target_type', '=', 'stage'),
                            ('target_type', '=', 'assigning'),
                        '|', ('ticket_type_id', '=', self.ticket_type_id.id), ('ticket_type_id', '=', False)]
          sla_polices = self.env['helpdesk.sla'].search(domain)
          res[sla] = sla_polices.filtered(lambda s: s.priority == sla.priority and s.tag_ids <= sla.tag_ids)

      return res

class LP_Helpdesk_Sla(models.Model):
  _inherit = 'helpdesk.sla'

  priority = fields.Selection(
      selection=[
      ('0', 'All'),
      ('1', 'Low priority'),
      ('2', 'Medium priority'),
      ('3', 'High priority'),
      ('4', 'Urgent'),
  ], string='Minimum Priority',
        default='0', required=True,
        help='Tickets under this priority will not be taken into account.')

class LP_Helpdesk_Sla_Report(models.Model):
  _inherit = 'helpdesk.sla.report.analysis'

  priority = fields.Selection(
      selection=[
      ('0', 'All'),
      ('1', 'Low priority'),
      ('2', 'Medium priority'),
      ('3', 'High priority'),
      ('4', 'Urgent'),
  ],  string='Minimum Priority', readonly=True)


class LP_Helpdesk_Affected_System(models.Model):
    _name = 'helpdesk.affected'
    _description = 'Helpdesk Affected System'
    _order = 'name'

    name = fields.Char('Affected System Name', required=True)


class LP_Clousure_Reoson(models.Model):
    _name = 'clousure.reason'
    _description = 'Clousure Reason'
    _order = 'name'

    name = fields.Char('Reason Name', required=True)

class LP_Helpdesk_Team(models.Model):

    _inherit='helpdesk.team'

    @api.model
    def retrieve_dashboard(self):
      dic_result = {
            'my_all': {'count': 0, 'hours': 0, 'failed': 0},
          'my_low': {'count': 0, 'hours': 0, 'failed': 0},
            'my_medium': {'count': 0, 'hours': 0, 'failed': 0},
            'my_high': {'count': 0, 'hours': 0, 'failed': 0},
            'my_urgent': {'count': 0, 'hours': 0, 'failed': 0},
        }

      tickets = self.env['helpdesk.ticket'].search_read(expression.AND([[('user_id', '=', self.env.uid)], [('stage_id.is_close', '=', False)]]),['sla_deadline', 'open_hours', 'sla_reached_late', 'priority'])

      def _get_round_hours(key):

          return  round(dic_result[key]['hours'] / (dic_result[key]['count'] or 1), 2)

      def _is_failed_sla(data):
          sla_deadline = fields.Datetime.now() > data.get('sla_deadline') if data.get('sla_deadline') else False
          return sla_deadline or data.get('sla_reached_late')

      def add_to(ticket, key="my_all"):
          dic_result[key]['count'] += 1
          dic_result[key]['hours'] += ticket['open_hours']
          if _is_failed_sla(ticket):
              dic_result[key]['failed'] += 1

      for ticket in tickets:
              add_to(ticket, 'my_all')
              if ticket['priority'] == '1':
                add_to(ticket,'my_low')
              if ticket['priority'] == '2':
                add_to(ticket,'my_medium')
              if ticket['priority'] == '3':
                  add_to(ticket, 'my_high')
              if ticket['priority'] == '4':
                  add_to(ticket, 'my_urgent')

      dic_result['my_low']['hours'] = _get_round_hours('my_low')
      dic_result['my_medium']['hours'] = _get_round_hours('my_medium')
      dic_result['my_all']['hours'] = _get_round_hours('my_all')
      dic_result['my_high']['hours'] = _get_round_hours('my_high')
      dic_result['my_urgent']['hours'] = _get_round_hours('my_urgent')

      res = super(LP_Helpdesk_Team, self).retrieve_dashboard()

      res.pop('my_all')
      res.pop('my_high')
      res.pop('my_urgent')

      result = {**dic_result, **res}


      return result
