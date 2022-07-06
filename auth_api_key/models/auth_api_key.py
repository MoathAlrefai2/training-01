# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import consteq
import string,random


class AuthApiKey(models.Model):
    _name = "auth.api.key"
    _description = "API Key"
    
    def _get_key(self):
        return ''.join([random.choice(string.ascii_lowercase) for n in range(25)])
    
    def _get_auto_key(self):
        key = self._get_key()
        exist_keys = self.search([]).mapped("key")
        while key in exist_keys:
            key = self._get_key()
        return key
         
    name = fields.Char(required=True)
    key = fields.Char(default=_get_auto_key,
        required=True,readonly=True,
        help="""The API key. Enter a dummy value in this field if it is
        obtained from the server environment configuration.""",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        help="""The user used to process the requests authenticated by
        the api key""",
    )
    active = fields.Boolean("Active", default=True)
    expiry_date = fields.Date("Expiry Date")
    
    _sql_constraints = [("name_uniq", "unique(name)", "Api Key name must be unique.")]

    @api.model
    def _retrieve_api_key(self, key):
        return self.browse(self._retrieve_api_key_id(key))

    @api.model
    def _retrieve_api_key_id(self, key):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("User is not allowed"))
        apis =  self.search([("active","=",True),('expiry_date','!=',False),('expiry_date','>',fields.Date.today())])
        for api_key in apis:
            if api_key.key and consteq(key, api_key.key):
                return api_key.id
        raise ValidationError(_("The key %s is not allowed") % key)

    @api.model
    def _retrieve_uid_from_api_key(self, key):
        return self._retrieve_api_key(key).user_id.id

