from odoo import models, fields, api
from odoo.exceptions import UserError


class LP_ASSET_MANAGEMENT(models.Model):
    _name = "asset.management"
    _description = "Assets Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "lp_name"
    
     
    lp_name = fields.Char("Name", required=True, tracking=True)
    lp_related_asset_id = fields.Many2one("account.asset", string="Related Asset", required=True, tracking=True)
    lp_used_by = fields.Selection([('employee','Employee'),('company','Company'),('department','Department')], string="Used By", inverse="_inverse_usage", tracking=True)
    lp_employee_id = fields.Many2one("hr.employee", string="Employee", inverse="_inverse_usage", tracking=True)
    lp_department_id = fields.Many2one("hr.department", string="Department", domain="[('lp_type', '=', 'department')]", inverse="_inverse_usage", tracking=True)
    lp_serial_number = fields.Char("Serial Number", tracking=True)
    lp_mac_address = fields.Char("MAC Address", tracking=True)
    lp_brand = fields.Char("Brand", tracking=True)
    lp_model = fields.Char("Model", tracking=True)
    lp_state = fields.Selection([('unassigned','Unassigned'),('assigned','Assigned'),('deprecated','Deprecated')], string="Status", default="unassigned", tracking=True)
    lp_acquisition_date = fields.Date("Acquisition Date", related="lp_related_asset_id.acquisition_date")
    lp_barcode = fields.Char("Barcode")
    lp_notes = fields.Text("Notes", tracking=True) 
    
    _sql_constraints = [
        (
            'unique_lp_related_asset_id', 'UNIQUE(lp_related_asset_id)',
            'The asset is already managed.')
    ]
    
    def _inverse_usage(self):
        for record in self:
            if (record.lp_used_by == "employee" and record.lp_employee_id):
                record.lp_state = "assigned"
                record.lp_department_id = False
            elif (record.lp_used_by == "department" and record.lp_department_id):
                record.lp_state = "assigned"
                record.lp_employee_id = False
            elif record.lp_used_by == "company":
                record.lp_state = "assigned"
                record.lp_employee_id = False
                record.lp_department_id = False
            else:
                record.lp_state = "unassigned"
                record.lp_employee_id = False
                record.lp_department_id = False
    
    def acrion_deprecate(self):
        self.write({'lp_state':'deprecated'})
                
