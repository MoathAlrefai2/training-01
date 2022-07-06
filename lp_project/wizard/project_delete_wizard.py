# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class LP_PROJECT_DELETE_WIZARD(models.TransientModel):
    _inherit = 'project.delete.wizard'

    def confirm_delete(self):
        res = super(LP_PROJECT_DELETE_WIZARD, self).confirm_delete()
        return self.env["ir.actions.actions"]._for_xml_id("project.open_view_project_all")
