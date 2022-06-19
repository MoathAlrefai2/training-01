import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError


# import tools


class Car(models.Model):
    _name = 'car.reserve'
    _description = 'Car Reserve'

    name = fields.Char('Name', required=True)
    price = fields.Float('Price for reserve')
    maker = fields.Char('Maker')
    color = fields.Char('Color')
    description = fields.Char('Description')
    img = fields.Binary("Car Image")
    made_date = fields.Integer("Made In")
    age_car = fields.Integer(
        string="Age Car",
        compute='_compute_age',
    )

    history = fields.Many2many('car.history', string='History ')

    reserved = fields.Many2one('res.users', string='Reserved')
    reserved_id = fields.Integer("reserved id")

    state = fields.Selection(
        [('new', 'NEW'),
         ('old', 'OLD'),
         ('expired', 'EXPIRED')],
        'State', default="new")
    state2 = fields.Selection(related="state")

    car_type = fields.Many2one('car.type', string='Car Type')

    transmission = fields.Selection(
        [('manual', 'Manual'),
         ('automatic', 'Automatic')],
        'Transmission', default="manual")

    fuel_type = fields.Selection(
        [('diesel', 'Diesel'),
         ('petrol_95', 'Petrol 95'),
         ('petrol_90', 'Petrol 90')],
        'Fuel Type', default="petrol_90")

    air_conditioning = fields.Boolean("Air Conditioning")

    # rating = fields.Integer("Rating")
    rating = fields.Selection([
        ('0', 'No Demand'),
        ('1', 'Low Demand'),
        ('2', 'Average Demand'),
        ('3', 'Average Demand2'),
        ('4', 'Average Demand3'),
        ('5', 'High Demand')], default="no")
    rating_count = fields.Integer("Rating Count")

    policies_fuel = fields.Selection(
        [('EfE', 'Empty For Empty'),
         ('LfL', 'Like For Like'),
         ('FfF', 'Full For Full')],
        'Policies Fuel', default="LfL")
    policies_miles = fields.Selection(
        [('basic', 'Basic-Limited To 150 KM Per Day'),
         ('plus', 'Basic-Limited To 250 KM Per Day'),
         ('premium', 'Unlimited KM Per Day'),
         ('premium_plus', 'Unlimited KM Per Day')],
        'Policies Miles', default="basic")
    policies_pick_up = fields.Selection(
        [('MAG', 'Meet And Greet'),
         ('OnA', 'On Airport'),
         ('OffA', 'Off Airport')],
        'Policies Pick Up', default="MAG")

    reserve_covered = fields.Many2many("car.covered", string="What Is Covered")

    @api.depends('made_date')
    def _compute_age(self):
        year_now =int(datetime.datetime.today().year)
        print(f"----------------{year_now}")
        for car in self:
            if car.made_date:
                delta = year_now - car.made_date
                car.age_car = delta
            else:
                car.age_car = 0

    def reserve_car(self,date_from,date_to):
        self.ensure_one()
        curent_user_id = self._context.get('uid')
        if self.reserved_id == 0:
            self.reserved = self.env['res.users'].search([('id', '=', curent_user_id)])
            self.reserved_id = curent_user_id
            reserved_from = date_from
            num_of_day = (date_to-date_from).days
            price = num_of_day * self.price
            name = self.reserved.name
            record = self.env['car.history'].create(
                {'user': curent_user_id, 'name': name, 'reserved_from': reserved_from,'reserved_to':date_to,'num_of_day': num_of_day,'price': price})
            self.history += record
        else:
            raise UserError("Sorry :( This Car is Reserved")

    def unreserve_car(self):
        self.ensure_one()
        curent_user_id = self._context.get('uid')
        curent_user = self.env['res.users'].search([('id', '=', curent_user_id)])
        all_records_in_history_this_car = self.history

        history_record = None
        for i in all_records_in_history_this_car:
            history_record = i

        if curent_user == history_record.user:
            self.reserved_id = 0
            self.reserved = None
            reserved_to = fields.Date.today()
            name = curent_user.name
            reserved_from = history_record.reserved_from
            num_of_day = (reserved_to - reserved_from).days
            price = num_of_day * self.price
            history_record.write({'reserved_to': reserved_to, 'num_of_day': num_of_day, 'price': price})

        else:
            raise UserError(
                f"Sorry ' {curent_user.name} ' You don't allow to 'Un reserve' this Car  This Car Is Reserved By Another User ' {history_record.user.name} '")

    def test(self):
        pass
