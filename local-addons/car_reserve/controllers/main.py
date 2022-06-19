# -*- coding: utf-8 -*-
import datetime

from odoo import http
from odoo.http import request

class Main(http.Controller):
    @http.route(['/my_cars',
                 '/my_cars/<string:view_mode>',
                 '/my_cars/<string:view_mode>/<string:filter>/<string:filter_by>',
                 '/my_cars/<string:view_mode>/<int:page>'], type='http', auth="user", website=True)
    def my_cars(self, view_mode=None, filter=None, filter_by=None, page=1):
        id_curent_user = request.uid
        # curent_user = request.env['res.users'].search([('id', '=', id_curent_user)])
        if view_mode == None:
            view_mode = "list_view"  # list_view

        if filter != None:
            if filter == "car_type":
                list_of_car = request.env['car.reserve'].search(['&',('car_type.name', '=', filter_by),('reserved_id', '=', id_curent_user)])
            if filter == "brand":
                list_of_car = request.env['car.reserve'].search(['&',('maker', '=', filter_by),('reserved_id', '=', id_curent_user)])
            if filter == "passengers":
                if filter_by == "1-2":
                    list_of_car = request.env['car.reserve'].search(
                        ['&','&', ('car_type.num_of_passengers', '>=', 1), ('car_type.num_of_passengers', '<=', 2),('reserved_id', '=', id_curent_user)])
                if filter_by == "3-5":
                    list_of_car = request.env['car.reserve'].search(
                        ['&', '&',('car_type.num_of_passengers', '>=', 3), ('car_type.num_of_passengers', '<=', 5),('reserved_id', '=', id_curent_user)])
                if filter_by == "6-8":
                    list_of_car = request.env['car.reserve'].search(
                        ['&', '&',('car_type.num_of_passengers', '>=', 6), ('car_type.num_of_passengers', '<=', 8),('reserved_id', '=', id_curent_user)])
                if filter_by == "9-11":
                    list_of_car = request.env['car.reserve'].search(
                        ['&','&', ('car_type.num_of_passengers', '>=', 9), ('car_type.num_of_passengers', '<=', 11),('reserved_id', '=', id_curent_user)])

        else:
            list_of_car = request.env['car.reserve'].search([('reserved_id', '=', id_curent_user)])

        num_of_page = 0
        if (len(list_of_car) % 10) != 0:
            num_of_page = (int(len(list_of_car) / 10)) + 1
        else:
            num_of_page = (int(len(list_of_car) / 10))

        return request.render(
            'car_reserve.my_cars', {
                'cars': list_of_car,
                'cars_length': len(list_of_car),
                'car_types': self.get_car_types(list_of_car),
                'car_brands': self.get_car_brands_and_num(list_of_car),
                'view_mode': view_mode,
                'num_of_page': num_of_page + 1,
                'page': page,
                'id_curent_user':id_curent_user
            })

        # return request.render(
        #     'car_reserve.cars', {
        #         'my_cars': request.env['car.reserve'].search([('reserved_id', '=', id_curent_user)]),
        #         'num_of_page': 1,
        #         'view_mode': "list_view",
        #         'page': 1,
        #     })

    @http.route(['/available_cars','/',
                 '/available_cars/<string:view_mode>',
                 '/available_cars/<string:view_mode>/<string:filter>/<string:filter_by>',
                 '/available_cars/<string:view_mode>/<int:page>']
        , type='http', auth="public", website=True)
    def available_cars(self, view_mode=None, filter=None, filter_by=None, page=1):

        if view_mode == None:
            view_mode = "list_view"  # list_view

        if filter != None:
            if filter == "car_type":
                list_of_car = request.env['car.reserve'].search([('car_type.name', '=', filter_by)])
            if filter == "brand":
                list_of_car = request.env['car.reserve'].search([('maker', '=', filter_by)])
            if filter == "passengers":
                if filter_by == "1-2":
                    list_of_car = request.env['car.reserve'].search(
                        ['&', ('car_type.num_of_passengers', '>=', 1), ('car_type.num_of_passengers', '<=', 2)])
                if filter_by == "3-5":
                    list_of_car = request.env['car.reserve'].search(
                        ['&', ('car_type.num_of_passengers', '>=', 3), ('car_type.num_of_passengers', '<=', 5)])
                if filter_by == "6-8":
                    list_of_car = request.env['car.reserve'].search(
                        ['&', ('car_type.num_of_passengers', '>=', 6), ('car_type.num_of_passengers', '<=', 8)])
                if filter_by == "9-11":
                    list_of_car = request.env['car.reserve'].search(
                        ['&', ('car_type.num_of_passengers', '>=', 9), ('car_type.num_of_passengers', '<=', 11)])

        else:
            list_of_car = request.env['car.reserve'].sudo().search([('reserved_id', '=', 0)])

        num_of_page = 0
        if (len(list_of_car) % 10) != 0:
            num_of_page = (int(len(list_of_car) / 10)) + 1
        else:
            num_of_page = (int(len(list_of_car) / 10))
        id_curent_user = -1
        if request.uid:
            id_curent_user=request.uid

        return request.render(
            'car_reserve.cars', {
                'cars': list_of_car,
                'cars_length': len(list_of_car),
                'car_types': self.get_car_types(list_of_car),
                'car_brands': self.get_car_brands_and_num(list_of_car),
                'view_mode': view_mode,
                'num_of_page': num_of_page + 1,
                'page': page,
                'id_curent_user': id_curent_user
            })

    @http.route('/car_info/<model("car.reserve"):car>', type='http', auth="public", website=True)
    def cars_info(self, car):
        id_curent_user=-1
        if request.uid:
            id_curent_user = request.uid
        car2 = request.env['car.reserve'].sudo().search([('id', '=', car.id)])

        return request.render(
            'car_reserve.cars_info', {
                'car': car2,  # request.env['car.reserve'].search([('id','=',6)]),
               'id_curent_user': id_curent_user,
            })

    @http.route('/reserve_car/<model("car.reserve"):car>', type='http', auth="user",methods=['POST'], website=True)
    def reserve_car(self, car,**post):
        date_from=datetime.datetime.strptime(post.get('date_from'),'%Y-%m-%d').date()
        date_to = datetime.datetime.strptime(post.get('date_to'),'%Y-%m-%d').date()

        id_curent_user = request.uid
        car.reserve_car(date_from,date_to)

        return request.redirect('/car_info/%s' % (car.id))

        # return request.render(
        #     'car_reserve.cars', {
        #         'cars': request.env['car.reserve'].search([('reserved_id', '=', id_curent_user)]),
        #     })

    @http.route('/unreserve_car/<model("car.reserve"):car>', type='http', auth="user", website=True)
    def unreserve_car(self, car):
        id_curent_user = request.uid
        car.unreserve_car()

        return request.redirect('/car_info/%s' % (car.id))

    def get_car_types(self, list_of_car):
        set_of_type = set()
        for car in list_of_car:
            set_of_type.add(car.car_type)
        return set_of_type

    def get_car_brands_and_num(self, list_of_car):
        set_of_brands = set()
        list_of_dict = []

        for car in list_of_car:
            set_of_brands.add(car.maker)

        for brand in set_of_brands:
            num_car_brand = 0
            for car in list_of_car:
                if brand == car.maker:
                    num_car_brand = num_car_brand + 1
            dict_of_brands_nad_num = {}
            dict_of_brands_nad_num["brand"] = brand
            dict_of_brands_nad_num["num"] = num_car_brand
            list_of_dict.append(dict_of_brands_nad_num)

        return list_of_dict
