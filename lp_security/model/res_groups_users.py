# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError , UserError


class LP_RES_USERS(models.Model):
    _inherit = 'res.users'
    
    lp_groups_id = fields.Many2many('res.groups', 'res_lp_groups_user_rel', 'uid', 'lgid', string='Groups')
    
    
    def _groups_consistent(self):
        for user in self:
            user.with_context(recurssivbely_update=True).lp_groups_id = [(4,g.id) \
                                    for g in user.groups_id.filtered(lambda x:x.show_group and x not in user.lp_groups_id)]
            
            
    
    def get_implied_groups(self,groups):
        self._cr.execute("""
                    WITH RECURSIVE group_imply(gid, hid) AS (
                        SELECT gid, hid
                          FROM res_groups_implied_rel
                         UNION
                        SELECT i.gid, r.hid
                          FROM res_groups_implied_rel r
                          JOIN group_imply i ON (i.hid = r.gid)
                    )
                    select hid from group_imply where gid in %(ids)s""", {'ids': tuple(groups)})
        dict = self._cr.fetchall()
        groups = [group[0] for group in dict]
        return self.env['res.groups'].browse(groups)
    
    def update_user_groups(self):
        for rec in self:
            inheritrd_groups = self.env["res.groups"]
            if rec.lp_groups_id:
                inheritrd_groups = rec.get_implied_groups(rec.lp_groups_id.ids)
            to_remove_groups = rec.groups_id.filtered(lambda x:x not in inheritrd_groups)
            if to_remove_groups:
                rec.groups_id -= to_remove_groups
            to_add_groups = rec.lp_groups_id - rec.groups_id
            rec.groups_id += to_add_groups
        
    
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(LP_RES_USERS, self).create(vals)
        res.update_user_groups()
        res._groups_consistent()
        for rec in res:
            rec.groups_id = rec.lp_groups_id
        return res
    

    def write(self, vals):
        res = super(LP_RES_USERS, self).write(vals)
        if "groups_id" in vals: 
            self._groups_consistent()
        if "lp_groups_id" in vals and not self._context.get("recurssivbely_update",False):
            self.update_user_groups()
            
        return res

class lp_RES_GROUPS(models.Model):
    _inherit = "res.groups"
    
    show_group = fields.Boolean("Show Group")
    
    
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(lp_RES_GROUPS, self).create(vals)
        res.users._groups_consistent()
        return res
        
        
    def write(self, vals):
        approver_group = self.env.ref('hr_holidays.group_hr_holidays_responsible', raise_if_not_found=False)
        if "users" in vals.keys() and self._context.get("force_leave_group",False) and any(approver_group.id == rec.id for rec in self):
            vals = {k:vals[k] for k in vals if k != "users"}
        res = super(lp_RES_GROUPS, self).write(vals)
        if "users" in vals.keys():
            self.users._groups_consistent()
        return res


            
        
    