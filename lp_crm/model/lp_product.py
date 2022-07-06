from odoo import models, fields, api


class LP_Product_Template(models.Model):
  _inherit = 'product.template'

  lp_resalable = fields.Boolean('Reseller (e.g. license)')