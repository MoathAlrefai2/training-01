from odoo import models, fields, api
from stdnum import pt



class LP_Department(models.Model):
    _inherit = ['hr.department']

    lp_type = fields.Selection([('director', 'Director'),
                                ('it_office', 'Office'),
                                ('department', 'Department'),
                                ('section', 'Section')],
                               'Type', default="section")

    lp_category = fields.Selection([('delivery', 'Delivery'),
                                ('operations', 'Operations'),
                                ('process_management', 'Process Management'),
                                ('quality_and_support', 'Quality & Support'),
                                ('sales_and_marketing','Sales & Marketing'),
                                ('accounting','Accounting')],
                               'Category')

    lp_analytic_account_group = fields.Many2one('account.analytic.group', string='Analytical Account Group')
    
    
    def get_child_department(self, parent_department):
        child_departmnet_data = []
        children_department_ids = self.env['hr.department'].search([('parent_id', '=', parent_department.id),('manager_id','!=',False)])
        if not children_department_ids:
            for employee in parent_department.member_ids:
                child_departmnet_data.append({ "name": employee.name,
                "Title": employee.job_title,
                'Department':employee.department_id.name,
                'JobDescription':'%'.join(employee.job_id.lp_job_description_ids.mapped("title")),
                "children": [],})
        else:
            for department in children_department_ids:
                children = self.get_child_department(department)
                
                child_departmnet_data.append({ "name": department.manager_id.name,
                "Title": department.manager_id.job_title,
                'Department':department.name,
                'JobDescription':'%'.join(department.manager_id.job_id.lp_job_description_ids.mapped("title")),
                "children": children,})
                
            for emp2 in parent_department.member_ids - parent_department.child_ids.mapped("manager_id"):
                    child_departmnet_data.append({ "name": emp2.name,
                "Title": emp2.job_title,
                'Department':parent_department.name,
                'JobDescription':'%'.join(emp2.job_id.lp_job_description_ids.mapped("title")),
                "children": [],})
        return child_departmnet_data
    
    
    @api.model
    def get_department_data_v2(self):
        final_total = 0
        Root_data = {}
        list_child = []
        top_department = self.env['hr.department'].search([('manager_id','!=',False),('parent_id', '=', False),('company_id','=',self.env.user.company_id.id)])
        department_data = {}
        for department in top_department:
            children = self.get_child_department(department)
            department_data = {
                "name": department.manager_id.name,
                "Title": department.manager_id.job_title,
                'Department':department.name,
                'JobDescription':'%'.join(department.manager_id.job_id.lp_job_description_ids.mapped("title")),
                "children": children,
            }
            list_child.append(department_data)
        return list_child
        return Root_data

