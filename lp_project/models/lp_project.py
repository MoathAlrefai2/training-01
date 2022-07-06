# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse, unquote
from odoo import models, fields, api
from odoo.exceptions import AccessError, ValidationError

# sudo pip3 install vsts
from vsts.vss_connection import VssConnection
from datetime import datetime

# sudo pip3 install msrest
from msrest.authentication import BasicAuthentication
from vsts.work_item_tracking.v4_1.models.wiql import Wiql

_logger = logging.getLogger(__name__)


class LP_Company(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        result = super(LP_Company, self).create(vals)
        tmp_sequence = {
            'name': 'Project Sequence',
            'code': 'project.project',
            'active': True,
            'padding': 4,
            'number_next': 1,
            'number_increment': 1,
            'company_id': result.id
        }

        self.env['ir.sequence'].create(tmp_sequence)

        return result


class LP_Project(models.Model):
    _inherit = ['project.project']

    lp_type = fields.Selection([('lp_fixed_time_price', 'Fixed Time/Price'),
                                ('lp_change_request', 'Change Request'),
                                ('lp_outsourcing', 'Outsourcing'),
                                ('lp_Inhouse', 'Inhouse')],
                               'Type', default="lp_fixed_time_price")
    lp_teams_link = fields.Char('TEAMS Channel')
    lp_devops_link = fields.Char('DevOps Project')
    lp_status = fields.Selection([('lp_new', 'New'),
                                  ('lp_in_progress', 'In Progress'),
                                  ('lp_closed', 'Closed')],
                                 'Status', default="lp_new")

    lp_category = fields.Selection([('delivery', 'Delivery'),
                                    ('opportunity', 'Opportunity'),
                                    ],
                                   'Category', default="delivery")

    lp_budget = fields.Char('Budget', readonly=True, tracking=True, copy=False)
    allowed_portal_user_ids = fields.Many2many('res.users', 'project_allowed_portal_users_rel',
                                               string="Project Team", domain=[('share', '=', True)])
    date_start = fields.Date(readonly=True, tracking=True, copy=False)
    lp_date_end = fields.Date('End Date', readonly=True, tracking=True, copy=False)
    lp_department = fields.Many2one('hr.department', string='Department', domain="[('lp_type', '=', 'department')]")
    lp_approver = fields.Many2one('res.users', string='Approver (Dept. Head)', tracking=True,
                                  related="lp_department.manager_id.user_id")
    lp_proposed_button = fields.Boolean('inv', compute='_onchange_propsed_button', default=False)
    lp_project_code = fields.Char(string="Project Code", readonly=True, required=True, copy=False, default=' ')
    lp_check_user_access = fields.Boolean('Check', compute='_check_access_pages', default=False)

    @api.onchange('lp_approver')
    def _compute_project_team_dept_head(self):
        if self.lp_approver.id:
            self.allowed_internal_user_ids = [(4, self.lp_approver.id)]
        if self.user_id.id:
            self.allowed_internal_user_ids = [(4, self.user_id.id)]

    @api.onchange('name')
    def _check_access_pages(self):
        if self.env.user.id == self.user_id.id or self.env.user.has_group(
                'project.group_project_manager') or self.env.user.id == self.lp_approver.id:
            self.lp_check_user_access = True
        else:
            self.lp_check_user_access = False

    @api.onchange('lp_approver')
    def _onchange_propsed_button(self):
        if self.env.user.id == self.lp_approver.id:
            self.lp_proposed_button = True
        else:
            self.lp_proposed_button = False

    @api.onchange('lp_department')
    def _onchange_lp_department(self):
        if self.lp_department:
            self.analytic_account_id.group_id = self.lp_department.lp_analytic_account_group

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = ['|', ('name', operator, name), ('lp_project_code', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def get_text_abbr(self, text):

        abbr = ''

        if text:
            list = text.split()
            for str in list:
                abbr = abbr + str[0]
        return abbr

    def get_dept_name_abbr(self, dept_id):
        dept_name_abbr = ''
        department_name = self.env['hr.department'].search([('id', '=', dept_id)]).name
        if department_name:
            dept_name_abbr = self.get_text_abbr(department_name)
        return dept_name_abbr

    def get_project_name_abbr(self, project_name):

        project_name_parts = project_name.split("_")  # Name & CR
        name_abbr = self.get_text_abbr(project_name_parts[0])
        if len(project_name_parts) > 1:
            return name_abbr + '_' + self.get_text_abbr(project_name_parts[1])
        return name_abbr

    def get_project_code(self, vals):
        project_code = ''
        next_sequence_num = self.get_next_sequence_number()
        dept_name_abbr = self.get_dept_name_abbr(self.get_department_id(vals))
        project_name = self.get_project_name(vals)
        project_name_abbr = self.get_project_name_abbr(project_name)
        if dept_name_abbr and project_name_abbr and next_sequence_num:
            project_code = 'LP_' + str(dept_name_abbr) + '_' + str(project_name_abbr) + '_' + str(next_sequence_num)
        return project_code

    def get_department_id(self, vals):

        if vals.get('lp_department'):
            return vals.get('lp_department')
        return self.lp_department.id

    def get_next_sequence_number(self):

        return self.env['ir.sequence'].next_by_code('project.project')

    def get_project_name(self, vals):
        if vals.get('name'):
            return vals.get('name')

        return self.name

    @api.model
    def create(self, vals):

        vals['lp_project_code'] = self.get_project_code(vals) or ' '
        result = super(LP_Project, self).create(vals)
        return result

    lp_proposed_budget = fields.Char('Proposed Budget', tracking=True, copy=False)
    lp_proposed_date_start = fields.Date('Proposed Start Date', tracking=True, copy=False)
    lp_proposed_date_end = fields.Date('Proposed End Date', tracking=True, copy=False)
    privacy_visibility = fields.Selection([
        ('followers', 'Invited internal users'),
        ('employees', 'All internal users'),
        ('portal', 'Invited portal users and all internal users'),
    ],
        string='Visibility', required=True,
        default='followers',
        help="Defines the visibility of the tasks of the project:\n"
             "- Invited internal users: employees may only see the followed project and tasks.\n"
             "- All internal users: employees may see all project and tasks.\n"
             "- Invited portal and all internal users: employees may see everything."
             "   Portal users may see project and tasks followed by\n"
             "   them or by someone of their company.")

    # DevOps fields
    lp_devops_token = fields.Char('Token')
    lp_devops_org_url = fields.Char('Organization URL', readonly=True)
    lp_devops_project_name = fields.Char('Project Name', readonly=True)
    _wit_client = None

    def notify_dept_head(self, message):
        if self.lp_proposed_budget or self.lp_proposed_date_start or self.lp_proposed_date_end:
            notification_ids = [(0, 0, {
                'res_partner_id': self.lp_approver.partner_id.id,
                'notification_type': 'inbox'
            })]
            self.message_post(
                body='Values proposed by ' + str(self.user_id.partner_id.name) + " :" + message + "need approval",
                message_type="notification",
                author_id=self.env.user.partner_id.id,
                notification_ids=notification_ids)

    def write(self, vals):

        if self.lp_project_code == ' ' or self.lp_project_code == 'New':
            vals['lp_project_code'] = self.get_project_code(vals) or ' '

        message = ""
        flag = False
        if 'lp_proposed_budget' in vals:
            message = message + "Proposed budget (" + str(vals['lp_proposed_budget']) + ") "
            flag = True
        if 'lp_proposed_date_start' in vals:
            message = message + "Proposed Start Date (" + str(vals['lp_proposed_date_start']) + ") "
            flag = True
        if 'lp_proposed_date_end' in vals:
            message = message + "Proposed End Date (" + str(vals['lp_proposed_date_end']) + ") "
            flag = True
        if flag:
            self.notify_dept_head(message)
        res = super(LP_Project, self).write(vals)
        return res

    @api.constrains('lp_devops_link')
    def _check_lp_devops_link(self):
        for record in self:
            if record.lp_devops_link:
                tmp_parsed_url = urlparse(record.lp_devops_link)
                tmp_path_parts = tmp_parsed_url.path.strip("/").split("/")
                if len(tmp_path_parts) != 2 or tmp_parsed_url.scheme == '' or tmp_parsed_url.netloc == '':
                    raise ValidationError(
                        'DevOps Project URL format is not valid. The valid format: http(s)://{domain}/{organization}/{project}')
                else:
                    record.lp_devops_org_url = tmp_parsed_url.scheme + "://" + tmp_parsed_url.netloc + "/" + \
                                               tmp_path_parts[0]
                    record.lp_devops_project_name = unquote(tmp_path_parts[1])
            else:
                record.lp_devops_org_url = ""
                record.lp_devops_project_name = ""

    def approve_proposed_values(self):
        self.ensure_one()
        is_admin = self.env.user.has_group('base.user_admin')
        if is_admin or (self.env.user.id == self.lp_approver.id):
            if self.lp_proposed_budget:
                self.lp_budget = self.lp_proposed_budget
            if self.lp_proposed_date_start:
                self.date_start = self.lp_proposed_date_start
            if self.lp_proposed_date_end:
                self.lp_date_end = self.lp_proposed_date_end
            self.lp_proposed_budget = ''
            self.lp_proposed_date_start = ''
            self.lp_proposed_date_end = ''
        else:
            raise AccessError('Only Admin or project\'s DH can approve the change')

    def insert_task(self, tmp_task):
        self.env['project.task'].sudo().create(tmp_task)
        return 1

    def update_task(self, tmp_task, task):
        count_update = 0
        if "lp_devops_changed_date" in tmp_task:
            if task.lp_devops_changed_date != tmp_task.get('lp_devops_changed_date'):
                task.write(tmp_task)
                count_update = count_update + 1
        return count_update

    def get_tags(self, work_item):
        tmp_tags = []
        if "System.Tags" in work_item.fields:
            tags = work_item.fields["System.Tags"]
            if tags:
                tags = tags.split("; ")
                for tag in tags:
                    lp_s = self.env['project.tags'].search([('name', '=', tag)])
                    if not lp_s:
                        self.env['project.tags'].sudo().create({'name': tag})
                    tmp_tags.append((4, lp_s[0].id))
        return tmp_tags

    def get_task(self, work_item):
        tmp_tags = self.get_tags(work_item)
        tmp_tags_id = {'tag_ids': tmp_tags}
        try:
            if tmp_tags:
                tmp_tags_id = {'tag_ids': tmp_tags}
        except:
            _logger.error('ERROR: Tag has a problem on this task!')
        tmp_description = ''
        tmp_TeamProject = ''
        tmp_Changedate = ''
        tmp_area = ''
        tmp_IterationPath = ''
        tmp_CreatedDate = ''
        tmp_OriginalEstimate = ''
        tmp_RemainingWork = ''
        tmp_CompletedWork = ''
        tmp_assigned_to = ''
        tmp_finish_date = ''
        tmp_priority = ''
        tmp_state = ''
        tmp_state_changedate = ''
        tags = ''
        tmp_task = {}
        if "Microsoft.VSTS.Common.StateChangeDate" in work_item.fields:
            if '.' in work_item.fields["Microsoft.VSTS.Common.StateChangeDate"]:
                tmp_state_changedate = datetime.strptime(work_item.fields["Microsoft.VSTS.Common.StateChangeDate"],
                                                         "%Y-%m-%dT%H:%M:%S.%fz")  # use striptime because there was a difference between time (odoo,devops)
            else:
                tmp_state_changedate = datetime.strptime(work_item.fields["Microsoft.VSTS.Common.StateChangeDate"],
                                                         "%Y-%m-%dT%H:%M:%Sz")
        else:
            tmp_state_changedate = False
        if "System.Description" in work_item.fields:
            tmp_description = work_item.fields["System.Description"]
        if "System.TeamProject" in work_item.fields:
            tmp_TeamProject = work_item.fields["System.TeamProject"]
        if "System.ChangedDate" in work_item.fields:
            if '.' in work_item.fields["System.ChangedDate"]:
                tmp_Changedate = datetime.strptime(work_item.fields["System.ChangedDate"],
                                                   "%Y-%m-%dT%H:%M:%S.%fz")  # use striptime cause there was a difference between time (odoo,devops)
            else:
                tmp_Changedate = datetime.strptime(work_item.fields["System.ChangedDate"], "%Y-%m-%dT%H:%M:%Sz")
        else:
            tmp_Changedate = False
        if "System.AreaPath" in work_item.fields:
            tmp_area = work_item.fields["System.AreaPath"]
        if "System.IterationPath" in work_item.fields:
            tmp_IterationPath = work_item.fields["System.IterationPath"]
        if "System.CreatedDate" in work_item.fields:
            tmp_CreatedDate = work_item.fields["System.CreatedDate"]
        if "Microsoft.VSTS.Common.ClosedDate" in work_item.fields:
            tmp_finish_date = work_item.fields["Microsoft.VSTS.Common.ClosedDate"]
        else:
            tmp_finish_date = False
        if "Microsoft.VSTS.Scheduling.OriginalEstimate" in work_item.fields:
            tmp_OriginalEstimate = work_item.fields["Microsoft.VSTS.Scheduling.OriginalEstimate"]
        if "Microsoft.VSTS.Scheduling.RemainingWork" in work_item.fields:
            tmp_RemainingWork = work_item.fields["Microsoft.VSTS.Scheduling.RemainingWork"]
        if "Microsoft.VSTS.Scheduling.CompletedWork" in work_item.fields:
            tmp_CompletedWork = work_item.fields["Microsoft.VSTS.Scheduling.CompletedWork"]
        if "System.AssignedTo" in work_item.fields:
            tmp_assigned_to = self.search_user(work_item.fields["System.AssignedTo"])
        if "Microsoft.VSTS.Common.Priority" in work_item.fields:
            tmp_priority = work_item.fields["Microsoft.VSTS.Common.Priority"]
        else:
            tmp_priority = False
        if "System.State" in work_item.fields:
            tmp_state = work_item.fields["System.State"]
            lp_stage = self.env['project.task.type'].search([('name', '=', tmp_state)])
            if not lp_stage:
                lp_stage = self.env['project.task.type'].create({'name': tmp_state})

        tmp_task = {
            'name': work_item.fields["System.Title"],
            'description': tmp_description,
            'lp_devops_completed_work': tmp_CompletedWork,
            'project_id': self.id,
            'stage_id': lp_stage[0].id,
            'lp_devops_project_name': tmp_TeamProject,
            'lp_devops_changed_date': tmp_Changedate,
            'lp_devops_area': tmp_area,
            'lp_devops_iteration': tmp_IterationPath,
            'lp_devops_start_date': tmp_CreatedDate,
            'lp_devops_original_estimate': tmp_OriginalEstimate,
            'planned_hours': tmp_OriginalEstimate,
            'lp_devops_remaining_work': tmp_RemainingWork,
            'lp_devops_finish_date': tmp_finish_date,
            'user_id': tmp_assigned_to,
            'lp_devops_priority': tmp_priority,
            'date_last_stage_update': tmp_state_changedate,
            'lp_task_state': tmp_state,
            'lp_devops_ref_id': work_item.id,
        }
        get_parent_task = self.get_task_parent(tmp_task.get('lp_devops_ref_id'))
        merge_dict = (tmp_task.update(tmp_tags_id))
        merge_dict = (tmp_task.update(get_parent_task))
        return tmp_task

    def get_task_parent(self, task_id):
        wit_client = self.get_wit_clients()
        source_id_1 = 0
        source_id_2 = 0
        source_id_3 = 0
        source_list = []
        tmp_req = ''
        tmp_parent = {}
        tmp_feature = ''
        tmp_parent_feature = {}
        tmp_epic = ''
        tmp_parent_epic = {}
        ess1 = Wiql(
            query=f""" select[System.Id], [System.WorkItemType], [System.Title], [System.AssignedTo], [System.State] from WorkItemLinks where ([System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward') and (Target.[System.Id] = '{task_id}') order by[System.Id] mode(Recursive, ReturnMatchingChildren)""")
        get_parent_list = wit_client.query_by_wiql(ess1).work_item_relations
        for sublist in get_parent_list:
            if sublist.target.id == task_id:
                if sublist.source:
                    source_id_1 = int(sublist.source.id)

        for sublist in get_parent_list:
            if sublist.target.id == source_id_1:
                if sublist.source:
                    source_id_2 = int(sublist.source.id)

        for sublist in get_parent_list:
            if sublist.target.id == source_id_2:
                if sublist.source:
                    source_id_3 = int(sublist.source.id)
        source_list.append(source_id_1)
        source_list.append(source_id_2)
        source_list.append(source_id_3)
        if source_list[0] != 0:
            wiql_parent_1 = wit_client.get_work_item(int(source_list[0]))
            if "System.Title" in wiql_parent_1.fields:
                if wiql_parent_1.fields["System.WorkItemType"] == 'Requirement':
                    tmp_req = wiql_parent_1.fields["System.Title"]
                    tmp_parent = {'lp_devops_requirement': tmp_req}
        if source_list[1] != 0:
            wiql_parent_2 = wit_client.get_work_item(int(source_list[1]))
            if "System.Title" in wiql_parent_2.fields:
                if wiql_parent_2.fields["System.WorkItemType"] == 'Feature':
                    tmp_feature = wiql_parent_2.fields["System.Title"]
                    tmp_parent_feature = {'lp_devops_feature': tmp_feature}
        if source_list[2] != 0:
            wiql_parent_3 = wit_client.get_work_item(int(source_list[2]))
            if "System.Title" in wiql_parent_3.fields:
                if wiql_parent_3.fields["System.WorkItemType"] == 'Epic':
                    tmp_epic = wiql_parent_3.fields["System.Title"]
                    tmp_parent_epic = {
                        'lp_devops_epic': tmp_epic
                    }

        merge_dict = (tmp_parent.update(tmp_parent_feature))
        merge_dict = (tmp_parent.update(tmp_parent_epic))

        return tmp_parent

    def get_wit_clients(self):
        if getattr(self, '_wit_client', None) is None:
            credentials = BasicAuthentication('', self.lp_devops_token)
            connection = VssConnection(base_url=self.lp_devops_org_url, creds=credentials)
            _wit_client = connection.get_client(
                'vsts.work_item_tracking.v4_1.work_item_tracking_client.WorkItemTrackingClient')
        return _wit_client

    def devops_sync(self):
        self.ensure_one()
        personal_access_token = self.lp_devops_token
        organization_url = self.lp_devops_org_url
        project_name = self.lp_devops_project_name
        if (not personal_access_token) or (not organization_url) or (not project_name):
            raise ValidationError('Please check you DevOps token and DevOps project URL')
        wiql = Wiql(
            query=f"""select [System.Id] From WorkItems Where [System.WorkItemType] = 'Task' AND [System.TeamProject] = '{project_name}' order by [System.Id] desc""")
        try:
            wit_client = self.get_wit_clients()
            wiql_results = wit_client.query_by_wiql(wiql).work_items
            check_workitem = False
            if not wiql_results:
                check_workitem = True
            count_insert = 0
            count_updates = 0
            count_error_task = 0
            if wiql_results:
                tasks_to_be_synced = []
                odoo_task_ids = self.env['project.task'].search([('project_id', '=', self.id)]).ids
                for task in self.env['project.task'].browse(odoo_task_ids):
                    try:
                        if task.lp_devops_ref_id:
                            work_item = wit_client.get_work_item(int(task.lp_devops_ref_id))
                            tmp_task = self.get_task(work_item)
                            count_updates = count_updates + self.update_task(tmp_task, task)
                            tasks_to_be_synced.append(task.lp_devops_ref_id)
                    except Exception as e:
                        count_error_task = count_error_task + 1
                        _logger.exception(e)
                tmp_devops_task = 0
                tasks_to_be_inserted = [wit_client.get_work_item(int(tmp_devops_task.id)) for tmp_devops_task in
                                        wiql_results if tmp_devops_task.id not in tasks_to_be_synced]
                for work_item in tasks_to_be_inserted:
                    try:
                        tmp_task = self.get_task(work_item)
                        count_insert = count_insert + self.insert_task(tmp_task)
                    except Exception as e:
                        count_error_task = count_error_task + 1
                        _logger.exception(e)
            return {
                'name': 'Information',
                'type': 'ir.actions.act_window',
                'res_model': 'project.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_lp_updates_counter': count_updates, 'default_lp_insert_counter': count_insert,
                            'default_lp_error_counter': count_error_task, 'default_lp_boolean': check_workitem,
                            'default_lp_get_project': self.lp_devops_project_name},
                'target': 'new'
            }
        except:
            raise ValidationError('Please check DevOps Token and DevOps Project URL!')

    def get_email(self, AssignedTo=''):
        email = ''
        try:
            AssignedTo = str(AssignedTo).split()
            email = AssignedTo[-1]
        except:
            _logger.error('ERROR: email not valid on this task!')
        return email.strip("<>")

    def search_user(self, AssignedTo=''):
        email = self.get_email(AssignedTo)
        users = self.env['res.users'].sudo().search([('login', '=', email)])
        if users:
            return users[0].id
        else:
            return self.user_id.id

    @api.model
    def _create_analytic_account_from_values(self, values):
        department_id = self.env['hr.department'].search([('id', '=', values.get('lp_department'))])
        res = super(LP_Project, self)._create_analytic_account_from_values(values)
        res['group_id'] = department_id.lp_analytic_account_group
        return res


class LP_Popup_Wizard(models.TransientModel):
    _name = 'project.wizard'
    _description = 'Pop up Wizard'
    lp_updates_counter = fields.Integer('Updated tasks:', readonly=True)
    lp_insert_counter = fields.Integer('Inserted tasks:', readonly=True)
    lp_error_counter = fields.Integer('Error tasks:', readonly=True)
    lp_boolean = fields.Boolean('check exist workitem')
    lp_get_project = fields.Char('project name')
