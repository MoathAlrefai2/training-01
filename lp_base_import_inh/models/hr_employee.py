from odoo import models, fields, api

class LP_Hr_Employee(models.Model):
    _inherit = ['hr.employee']
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            operator = 'ilike'
            args = ['|',('name', operator, name),('work_email',operator,name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)