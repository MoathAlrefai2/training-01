from odoo import models, fields, api
from odoo.osv import expression


class LP_ASEET_TYPE(models.Model):
    _name = "asset.type"
    _description = "Asset Type"
    _rec_name = "lp_name" 
     
    lp_name = fields.Char("Name", required=True)
    
    
class LP_ASSET_ACCOUNT_ASSET(models.Model):
    _inherit = "account.asset"
    
    lp_type_id = fields.Many2one("asset.type", string="Type")
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get("asset_management",False):
            managed_assets = self.env["asset.management"].search([]).mapped('lp_related_asset_id.id')
            domain = [('id', 'not in', managed_assets)]
            if args == None:
                args = domain
            else:
                args = expression.AND([domain, args])
        return super(LP_ASSET_ACCOUNT_ASSET, self).name_search(name, args, operator, limit)
                