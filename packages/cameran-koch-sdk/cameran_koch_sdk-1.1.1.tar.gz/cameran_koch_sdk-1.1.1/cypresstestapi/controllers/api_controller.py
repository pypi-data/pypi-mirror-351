# -*- coding: utf-8 -*-

"""
cypresstestapi

This file was automatically generated for Newtest by APIMATIC v3.0 (
 https://www.apimatic.io ).
"""

from cypresstestapi.api_helper import APIHelper
from cypresstestapi.configuration import Server
from cypresstestapi.http.api_response import ApiResponse
from cypresstestapi.controllers.base_controller import BaseController
from apimatic_core.request_builder import RequestBuilder
from apimatic_core.response_handler import ResponseHandler
from apimatic_core.types.parameter import Parameter
from cypresstestapi.http.http_method_enum import HttpMethodEnum
from cypresstestapi.models.item import Item
from cypresstestapi.exceptions.api_exception import APIException


class APIController(BaseController):

    """A Controller to access Endpoints in the cypresstestapi API."""
    def __init__(self, config):
        super(APIController, self).__init__(config)

    def create_o_auth_token(self,
                            body=None):
        """Does a POST request to /tokens.

        Generates a new OAuth token with the specified scopes.

        Args:
            body (TokensRequest, optional): The request body parameter.

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. OAuth
                token created successfully

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        return super().new_api_call_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/tokens')
            .http_method(HttpMethodEnum.POST)
            .header_param(Parameter()
                          .key('Content-Type')
                          .value('application/json'))
            .body_param(Parameter()
                        .value(body))
            .body_serializer(APIHelper.json_serialize)
        ).response(
            ResponseHandler()
            .is_api_response(True)
            .local_error('400', 'Bad request', APIException)
        ).execute()

    def createanitem(self,
                     status,
                     body=None):
        """Does a POST request to /items/{status}.

        Creates a new resource in the system.

        Args:
            status (Status3Enum): The status of the items to filter by.
            body (Item, optional): Custom model with additional properties

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Example
                response

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        return super().new_api_call_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/items/{status}')
            .http_method(HttpMethodEnum.POST)
            .template_param(Parameter()
                            .key('status')
                            .value(status)
                            .is_required(True)
                            .should_encode(True))
            .header_param(Parameter()
                          .key('Content-Type')
                          .value('application/json'))
            .body_param(Parameter()
                        .value(body))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
            .body_serializer(APIHelper.json_serialize)
        ).response(
            ResponseHandler()
            .deserializer(APIHelper.json_deserialize)
            .is_api_response(True)
            .local_error('400', 'Bad Syntax', APIException)
            .local_error('401', 'Unauthorized', APIException)
            .local_error('403', 'Permission Denied', APIException)
        ).execute()

    def getanitemby_id(self,
                       id,
                       value):
        """Does a GET request to /items/{id}.

        Args:
            id (str): The ID of the item to retrieve
            value (str): The value of the item to retrieve

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Item
                retrieved successfully

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        return super().new_api_call_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/items/{id}')
            .http_method(HttpMethodEnum.GET)
            .template_param(Parameter()
                            .key('id')
                            .value(id)
                            .is_required(True)
                            .should_encode(True))
            .query_param(Parameter()
                         .key('value')
                         .value(value)
                         .is_required(True))
            .header_param(Parameter()
                          .key('accept')
                          .value('application/json'))
        ).response(
            ResponseHandler()
            .deserializer(APIHelper.json_deserialize)
            .deserialize_into(Item.from_dictionary)
            .is_api_response(True)
        ).execute()

    def test_endpointwith_arrays(self,
                                 body=None):
        """Does a POST request to /multiple-arrays.

        This endpoint accepts a complex structure with multiple arrays.

        Args:
            body (MultipleArraysRequest, optional): The request body parameter.

        Returns:
            ApiResponse: An object with the response value as well as other
                useful information such as status codes and headers. Request
                processed successfully

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """

        return super().new_api_call_builder.request(
            RequestBuilder().server(Server.DEFAULT)
            .path('/multiple-arrays')
            .http_method(HttpMethodEnum.POST)
            .header_param(Parameter()
                          .key('Content-Type')
                          .value('application/json'))
            .body_param(Parameter()
                        .value(body))
            .body_serializer(APIHelper.json_serialize)
        ).response(
            ResponseHandler()
            .is_api_response(True)
            .local_error('400', 'Bad request', APIException)
        ).execute()
