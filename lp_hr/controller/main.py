# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class EmployeeChart(http.Controller):

    @http.route('/get_organization_chart', type='json', method="POST", auth='api_key',cors='*',csrf=False)
    def get_organization_chart(self):
        dept_data = request.env["hr.department"].get_department_data_v2()
        result = {"status_code":200,"data":dept_data}
        return result
