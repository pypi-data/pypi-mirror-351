import os
import re
import socket
import time
from types import SimpleNamespace
from typing import List, Optional, Dict

from flask import Flask, request, Response, g
from flask_opsgenie.opsgenie import raise_opsgenie_alert
from flask_opsgenie.entities import AlertType
from flask_opsgenie.entities import OpsgenieAlertParams
from http import HTTPStatus

CONFIG_ALERT_STATUS_CODES = "ALERT_STATUS_CODES"
CONFIG_ALERT_STATUS_CLASSES = "ALERT_STATUS_CLASSES"
CONFIG_MONITORED_ENDPOINTS = "MONITORED_ENDPOINTS"
CONFIG_IGNORED_ENDPOINTS = "IGNORED_ENDPOINTS"
CONFIG_THRESHOLD_RESPONSE_TIME = "THRESHOLD_RESPONSE_TIME"
CONFIG_RESPONSE_TIME_MONITORED_ENDPOINTS = "RESPONSE_TIME_MONITORED_ENDPOINTS"
CONFIG_OPSGENIE_TOKEN = "OPSGENIE_TOKEN"
CONFIG_ALERT_TAGS = "ALERT_TAGS"
CONFIG_ALERT_DETAILS = "ALERT_DETAILS"
CONFIG_ALERT_PRIORITY = "ALERT_PRIORITY"
CONFIG_ALERT_ALIAS = "ALERT_ALIAS"
CONFIG_ALERT_STATUS_ALIAS = "ALERT_STATUS_ALIAS"
CONFIG_ALERT_LATENCY_ALIAS = "ALERT_LATENCY_ALIAS"
CONFIG_ALERT_EXCEPTION_ALIAS = "ALERT_EXCEPTION_ALIAS"
CONFIG_RESPONDER = "RESPONDER"
CONFIG_OPSGENIE_API_BASE = "OPSGENIE_API_BASE"
CONFIG_SERVICE_ID = "SERVICE_ID"
CONFIG_ALERT_EXCEPTION = "ALERT_EXCEPTION"
CONFIG_NO_TRACEBACK = "NO_TRACEBACK"
CONFIG_FORWARDED_HEADER_KEYS = "FORWARDED_HEADER_KEYS"
OPSGENIE_API_BASE_US = "https://api.opsgenie.com"
ENVTYPE = "ENVTYPE"


class FlaskOpsgenie(object):

    def __init__(self, app: Optional[Flask]):

        self.app = app
        self._host = None
        self._alert_status_codes = None
        self._alert_status_classes = None
        self._monitored_endpoints = None
        self._ignored_endpoints = None
        self._threshold_response_time = None
        self._response_time_monitored_endpoints = None
        self._opsgenie_token = None
        self._alert_tags = None
        self._alert_details = None
        self._alert_priority = None
        self._alert_alias = None
        self._alert_status_alias = None
        self._alert_latency_alias = None
        self._alert_exception_alias = None
        self._responder = None
        self._opsgenie_api_base = None
        self._service_id = None
        self._forwarded_header_keys = None
        self._request_headers = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):

        self._alert_status_codes =  [int(x) for x in app.config.get(CONFIG_ALERT_STATUS_CODES, [])]
        self._alert_status_classes = app.config.get(CONFIG_ALERT_STATUS_CLASSES)
        self._monitored_endpoints = app.config.get(CONFIG_MONITORED_ENDPOINTS)
        self._ignored_endpoints = app.config.get(CONFIG_IGNORED_ENDPOINTS)
        self._threshold_response_time = app.config.get(CONFIG_THRESHOLD_RESPONSE_TIME)
        self._response_time_monitored_endpoints = app.config.get(CONFIG_RESPONSE_TIME_MONITORED_ENDPOINTS)
        self._opsgenie_token = app.config.get(CONFIG_OPSGENIE_TOKEN)
        self._alert_tags = app.config.get(CONFIG_ALERT_TAGS)
        self._alert_details = app.config.get(CONFIG_ALERT_DETAILS, {})
        self._alert_alias = app.config.get(CONFIG_ALERT_ALIAS)
        self._alert_status_alias = app.config.get(CONFIG_ALERT_STATUS_ALIAS, self._alert_alias)
        self._alert_latency_alias = app.config.get(CONFIG_ALERT_LATENCY_ALIAS, self._alert_alias)
        self._alert_exception_alias = app.config.get(CONFIG_ALERT_EXCEPTION_ALIAS, self._alert_alias)
        self._alert_priority = app.config.get(CONFIG_ALERT_PRIORITY, "P4")
        self._responder = app.config.get(CONFIG_RESPONDER)
        self._opsgenie_api_base = app.config.get(CONFIG_OPSGENIE_API_BASE, OPSGENIE_API_BASE_US)
        self._service_id = app.config.get(CONFIG_SERVICE_ID)
        self._alert_exception = app.config.get(CONFIG_ALERT_EXCEPTION, False)
        self._no_traceback = app.config.get(CONFIG_NO_TRACEBACK, False)
        self._forwarded_header_keys = app.config.get(CONFIG_FORWARDED_HEADER_KEYS, False)
        self._envtype = app.config.get(ENVTYPE, "local")
        self._host = socket.gethostname()

        # pre-process status_class list if present
        if self._alert_status_classes:
            self._alert_status_classes = [s_class.upper() for s_class in self._alert_status_classes]

        # add host and service to alert details as well
        self._alert_details["host"] = self._host
        self._alert_details["service_id"] = self._service_id

        app.before_request(self._before_request)
        app.after_request(self._after_request)

    def opsgenie_params_util(self) -> OpsgenieAlertParams:

        return OpsgenieAlertParams(
            opsgenie_token=self._opsgenie_token,
            alert_tags=self._alert_tags,
            alert_details=self._alert_details,
            alert_alias=self._alert_alias,
            alert_status_alias=self._alert_status_alias,
            alert_latency_alias=self._alert_latency_alias,
            alert_exception_alias=self._alert_exception_alias,
            no_traceback = self._no_traceback,
            alert_priority=self._alert_priority,
            alert_responder=self._responder,
            opsgenie_api_base=self._opsgenie_api_base,
            envtype=self._envtype
        )

    def _get_status_class(self, status_code: int) -> str:
        return str(status_code)[0] + "XX"

    def _path_present(self, endpoint:str, endpoint_patterns:List[str]):
        match_results = [False if re.match(pattern, endpoint) == None else True for pattern in endpoint_patterns]
        return any(match_results)

    def _before_request(self):
        self._request_headers = request.headers
        g._flask_opsgenie = SimpleNamespace()
        g._flask_opsgenie._flask_request_begin_at = time.time()

    def _after_request(self, response: Response):
        elapsed_time = (time.time() - g._flask_opsgenie._flask_request_begin_at) * 1000

        status_code = response.status_code

        # get value if status code is of type enum HTTPStatus
        status_code = status_code.value if type(status_code) == HTTPStatus else status_code
        status_class = self._get_status_class(status_code)
        endpoint = request.path

        # Fetching Request header values
        extra_props = self._extract_request_header()

        if (self._alert_status_codes and status_code in self._alert_status_codes) or \
                (self._alert_status_classes and status_class in self._alert_status_classes):
            if (self._monitored_endpoints and self._path_present(endpoint, self._monitored_endpoints)) or \
                    (not self._monitored_endpoints and not(self._ignored_endpoints and self._path_present(endpoint, self._ignored_endpoints))):
                if self._alert_status_codes and status_code in self._alert_status_codes:

                    raise_opsgenie_alert(AlertType.STATUS_ALERT, alert_status_code=status_code,
                                         opsgenie_alert_params=self.opsgenie_params_util(), response_status_code=status_code,
                                         extra_props=extra_props)

                elif self._alert_status_classes and status_class in self._alert_status_classes:
                    raise_opsgenie_alert(AlertType.STATUS_ALERT, alert_status_class=status_class,
                                         opsgenie_alert_params=self.opsgenie_params_util(), response_status_code=status_code,
                                         extra_props=extra_props)

        if self._threshold_response_time and self._response_time_monitored_endpoints and \
                self._path_present(endpoint, self._response_time_monitored_endpoints) \
                and elapsed_time > self._threshold_response_time:

            raise_opsgenie_alert(AlertType.LATENCY_ALERT, elapsed_time=elapsed_time, alert_status_code=status_code,
                                 opsgenie_alert_params=self.opsgenie_params_util(), extra_props=extra_props)

        return response

    def raise_exception_alert(self, alert_type:AlertType = None, exception=None, func_name:str=None,
                              extra_props: Dict[str,str] = {}, alert_priority: str = ''):

        # Fetching Request header values
        header_details = self._extract_request_header()
        extra_props = {**extra_props, **header_details}

        raise_opsgenie_alert(alert_type=alert_type, exception=exception, func_name=func_name, opsgenie_alert_params=self.opsgenie_params_util(),
                             extra_props=extra_props, alert_priority=alert_priority)

    def raise_gevent_exception_alert(self, greenlet):
        try:
            greenlet.get()
        except Exception as e:
            # Fetching Request header values
            extra_props = self._extract_request_header()
            self.raise_exception_alert(alert_type=AlertType.MANUAL, exception=e, func_name="gevent", extra_props=extra_props)

    def gevent_exception_callback(self, g):
        g.link_exception(self.raise_gevent_exception_alert)


    def _extract_request_header(self):
        extra_props = {}
        if self._forwarded_header_keys:
            for header_key in self._forwarded_header_keys:
                extra_props[header_key] = self._request_headers.get(header_key, None)

        return extra_props