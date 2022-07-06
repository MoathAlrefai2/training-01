# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError , UserError
    
class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'

    email = fields.Char(string='Email', compute='_compute_email_phone', groups="sales_team.group_sale_salesman")
    mobile = fields.Char(string='Mobile Phone', compute='_compute_email_phone', groups="sales_team.group_sale_salesman")


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
     
    @api.model
    def _timesheet_preprocess(self, values):
        res = super(AccountAnalyticLine, self.sudo())._timesheet_preprocess(values)
        return res


class LP_Task(models.Model):
    _inherit = "project.task"
    
    partner_id = fields.Many2one(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    email_from = fields.Char(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    ribbon_message = fields.Char(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    display_create_order = fields.Boolean(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    sale_line_id = fields.Many2one(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    


class LP_HR_EMPLOYEE(models.Model):
    _inherit = "hr.employee"
    
    category_ids = fields.Many2many(groups="hr.group_hr_manager,hr.group_hr_user")


class LP_HR_EMPLOYEE_PUBLIC(models.Model):
    _inherit = 'hr.employee.public'
    
    address_id = fields.Many2one( groups='lp_security.lp_group_access_not_private_contact')
    

class LP_HR_EMPLOYEE(models.Model):
    _inherit = 'hr.employee'
    
    
    @api.model
    def create(self, values):
        return super(LP_HR_EMPLOYEE, self.with_context(force_leave_group=True)).create(values)
    
    def write(self, values):
        return super(LP_HR_EMPLOYEE, self.with_context(force_leave_group=True)).write(values)
    
    
class LP_MAIL_THREAD(models.AbstractModel):
    _inherit = 'mail.thread'

    message_partner_ids = fields.Many2many(
        groups='lp_security.lp_group_access_not_private_contact,base.group_private_addresses')
     
    message_follower_ids = fields.One2many(groups='lp_security.lp_group_access_not_private_contact,base.group_private_addresses')
    message_ids = fields.One2many(
        groups='lp_security.lp_group_access_not_private_contact,base.group_private_addresses')


class LP_PROJECT_PROJECT(models.Model):
    _inherit = 'project.project'
    
    partner_id = fields.Many2one(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    partner_email = fields.Char(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    partner_phone = fields.Char(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    display_create_order = fields.Boolean(groups="lp_security.lp_group_access_not_private_contact,base.group_private_addresses")
    
    def add_followers(self):
        users = self.env["res.users"]
        hr_users = self.env.ref("lp_security.hr_manager")
        hr_senior_officer = self.env.ref("lp_security.hr_senior_officer")
        hr_officer = self.env.ref("lp_security.hr_officer")
        ch_accounting = self.env.ref("lp_security.cheif_accountant_group")
        accounting_officer = self.env.ref("lp_security.accounting_officer_group")
        if hr_users:
            users += hr_users.users
        if hr_officer:
            users += hr_officer.users
        if hr_senior_officer:
            users += hr_senior_officer.users
        if  accounting_officer:
            users += accounting_officer.users
        if  ch_accounting:
            users += ch_accounting.users
        self.message_subscribe(partner_ids=users.mapped("partner_id.id"))
    
    @api.model
    def create(self, values):
        res = super(LP_PROJECT_PROJECT, self).create(values)
        res.add_followers()
        return res
        
    