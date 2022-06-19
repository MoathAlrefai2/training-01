from odoo import models, fields,api
import logging


logger = logging.getLogger()

formatee = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
file_handler=logging.FileHandler("log.log")
file_handler.setFormatter(formatee)
logger.addHandler(file_handler)
handlers = logging.getLogger().handlers
print(f"------------------BRINT------------{handlers[1].__dict__}")

print(f"------------------BRINT------------{handlers[0].__dict__}")
logger.debug("EEEEEEEEEEEEEE")
# import tools


class User(models.Model):

    _inherit = 'res.users'
    whish_list = fields.Many2one('car.whishlist',string="reserved list")





