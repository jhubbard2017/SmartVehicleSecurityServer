# -*- coding: utf-8 -*-
#
# connections module
#

from flask import request
from securityserverpy import _logger
from securityserverpy.routes import verify_request, error_response, success_response, database, app


class Connections(object):

    _ROOT_PATH = '/connections'

    def __init__(self):

        # User inner methods so self pointer can be accessed

        @app.route('{0}/add'.format(self._ROOT_PATH), methods=['POST'])
        def add_connection():
            """add connection for system

            required_data:
                system_id: str
                host: str
                port: int
            """
            required_data_keys = ['system_id', 'host', 'port']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            if database.get_connection(request.json['system_id']):
                return error_response('Connection already exist for system')

            if not database.add_connection(request.json['system_id'], request.json['host'], request.json['port']):
                return error_response('Unable to add connection')

            return success_response(request.path)

        @app.route('{0}/get'.format(self._ROOT_PATH), methods=['POST'])
        def get_connection():
            """get connection for system

            required_data:
                system_id: str
            """
            required_data_keys = ['system_id']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            connection = database.get_connection(request.json['system_id'])
            if not connection: return success_response(request.path, data=False)

            return success_response(request.path, data=connection)

        @app.route('{0}/update'.format(self._ROOT_PATH), methods=['POST'])
        def update_connection():
            """update connection for system

            required_data:
                system_id: str
                host: str
                port: int
            """
            required_data_keys = ['system_id', 'host', 'port']
            status, error = verify_request(request.json, keys=required_data_keys, all_should_exist=True)
            if not status: return error_response(error)

            if not database.get_connection(request.json['system_id']):
                return error_response('Connection for system does not exist')

            if not database.update_connection(request.json['system_id'], host=request.json['host'], port=request.json['port']):
                return error_response('Unable to update connection for system')

            return success_response(request.path)