import logging
import requests
import sys
from requests import HTTPError
import traceback
from typing import Any, Dict, Optional
from flask import request
from flask_opsgenie.entities import AlertType, OpsgenieAlertParams, AlertPriority

logger = logging.getLogger(__name__)

def __exception_to_string(exception: Exception) -> str:
    try:
        return str(exception)
    except RecursionError:
        '''
        On some cases when an exception is raised from another exception
        for example:
        try:
            a = 1/0
        exception Exception as e:
            raise MyException() from e
        if we try to call str on the raised MyException then
        python throws:
        RecursionError: maximum recursion depth exceeded while getting the str of an object
        Hence we handle that case here by returning the topmost exception
        from the traceback list.
        '''
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            trace_back = traceback.format_exception(exception)
        else:
            trace_back = traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__)
        return trace_back[-1]

def make_opsgenie_api_request(http_verb:str="get", url:str=None, payload:Dict[str, Any]=None, opsgenie_token:str=None):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'GenieKey {opsgenie_token}'
    }

    response = getattr(requests, http_verb)(
        url, headers=headers, json=payload
    )
    response.raise_for_status()


def raise_opsgenie_status_alert(alert_status_code:Optional[str] = None, alert_status_class:Optional[str] = None,
                                opsgenie_alert_params:OpsgenieAlertParams=None, response_status_code: int=None, extra_props:Dict[str, str] = {}):

    endpoint = request.path
    url = request.url
    method = request.method
    summary = ""
    description = ""

    # add url info into details
    opsgenie_alert_params.alert_details["endpoint"] = endpoint
    opsgenie_alert_params.alert_details["url"] = url
    opsgenie_alert_params.alert_details["method"] = method

    # Add header values to alert_details
    opsgenie_alert_params.alert_details = {**opsgenie_alert_params.alert_details, **extra_props}

    # update the status code/class as well in details, will help in searching
    if alert_status_code:
        opsgenie_alert_params.alert_details["status_code"] = alert_status_code
    else:
        opsgenie_alert_params.alert_details["status_class"] = alert_status_class

    # update alias if not set
    # Alias: serviceID-<path>-<status-code>-ALERT_STATUS_ALIAS
    alias = f'{opsgenie_alert_params.alert_details["service_id"]}-{request.path}-{response_status_code}-{opsgenie_alert_params.envtype}'
    if opsgenie_alert_params.alert_status_alias:
        opsgenie_alert_params.alert_status_alias = alias + "-" + opsgenie_alert_params.alert_status_alias
    else:
        opsgenie_alert_params.alert_status_alias =  alias

    if alert_status_code:
        summary = f'{endpoint} returned unaccepted status code : {alert_status_code} | Alert generated from {opsgenie_alert_params.alert_details["service_id"]}'
        description = f'{endpoint} returned status code : {alert_status_code}. Complete URL : {url} called with method ' \
                      f'{method}. Endpoint served by service : {opsgenie_alert_params.alert_details["service_id"]} on host: ' \
                      f'{opsgenie_alert_params.alert_details["host"]}'
    if alert_status_class:
        summary = f'{endpoint} returned unaccepted status class : {alert_status_class} | Alert generated from flask'
        description = f'{endpoint} returned status code from class : {alert_status_class}. Complete URL : {url} called with method ' \
                      f'{method}. Endpoint served by service : {opsgenie_alert_params.alert_details["service_id"]} on host: ' \
                      f'{opsgenie_alert_params.alert_details["host"]}'

    payload = {
        "message": summary,
        "description": description,
        "alias": opsgenie_alert_params.alert_status_alias,
        "tags": opsgenie_alert_params.alert_tags,
        "details": opsgenie_alert_params.alert_details,
        "priority": opsgenie_alert_params.alert_priority.value,
    }

    # add responders if present
    if opsgenie_alert_params.alert_responder:
        payload["responders"] = opsgenie_alert_params.alert_responder

    # Now we are all set to make the alert api call to opsgenie
    try:
        make_opsgenie_api_request(
            http_verb="post", url=f'{opsgenie_alert_params.opsgenie_api_base}/v2/alerts', payload=payload,
            opsgenie_token=opsgenie_alert_params.opsgenie_token
        )
    except Exception as e:
        logger.exception(e)


def raise_opsgenie_latency_alert(elapsed_time:int, alert_status_code:int, opsgenie_alert_params:OpsgenieAlertParams=None, extra_props:Dict[str, str] = {}):
    endpoint = request.path
    url = request.url
    method = request.method

    # add url info into details
    opsgenie_alert_params.alert_details["endpoint"] = endpoint
    opsgenie_alert_params.alert_details["url"] = url
    opsgenie_alert_params.alert_details["method"] = method
    opsgenie_alert_params.alert_details["status_code"] = alert_status_code

    # Add header values to alert_details
    opsgenie_alert_params.alert_details = {**opsgenie_alert_params.alert_details, **extra_props}

    # update alias if not set
    alias = f'{opsgenie_alert_params.alert_details["service_id"]}-response-latency-alert-{opsgenie_alert_params.envtype}'
    if not opsgenie_alert_params.alert_latency_alias:
        opsgenie_alert_params.alert_latency_alias = alias
    else:
        opsgenie_alert_params.alert_latency_alias = f"{opsgenie_alert_params.alert_exception_alias}-{alias}"

    summary = f'{endpoint} showed unexpected response time : {elapsed_time}ms | Alert generated from flask'
    description = f'{endpoint} showed unexpected response time : {elapsed_time}ms. Complete URL : {url} called with method ' \
                    f'{method}. Endpoint served by service : {opsgenie_alert_params.alert_details["service_id"]} on host: ' \
                    f'{opsgenie_alert_params.alert_details["host"]}'

    payload = {
        "message": summary,
        "description": description,
        "alias": opsgenie_alert_params.alert_latency_alias,
        "tags": opsgenie_alert_params.alert_tags,
        "details": opsgenie_alert_params.alert_details,
        "priority": opsgenie_alert_params.alert_priority.value,
    }

    # add responders if present
    if opsgenie_alert_params.alert_responder:
        payload["responders"] = opsgenie_alert_params.alert_responder

    # Now we are all set to make the alert api call to opsgenie
    try:
        make_opsgenie_api_request(
            http_verb="post", url=f'{opsgenie_alert_params.opsgenie_api_base}/v2/alerts', payload=payload,
            opsgenie_token=opsgenie_alert_params.opsgenie_token
        )
    except Exception as e:
        logger.exception(e)


def raise_opsgenie_exception_alert(exception:Exception=None, opsgenie_alert_params:OpsgenieAlertParams=None,
                                   extra_props: Dict[str,str] = {}):

    endpoint = request.path
    url = request.url
    method = request.method

    # add url info into details
    opsgenie_alert_params.alert_details["endpoint"] = endpoint
    opsgenie_alert_params.alert_details["url"] = url
    opsgenie_alert_params.alert_details["method"] = method
    opsgenie_alert_params.alert_details["exception"] = __exception_to_string(exception)

    # merge existing details dict with extra_props
    opsgenie_alert_params.alert_details = {**opsgenie_alert_params.alert_details, **extra_props}

    # update alias if not set
    # Alias: serviceid-<path>-<exception-name>-ALERT_EXCEPTION_ALIAS
    alias = f'{opsgenie_alert_params.alert_details["service_id"]}-{endpoint}-{exception.__class__.__name__}-{opsgenie_alert_params.envtype}'
    if opsgenie_alert_params.alert_exception_alias:
        opsgenie_alert_params.alert_exception_alias = alias + "-" + opsgenie_alert_params.alert_exception_alias
    else:
        opsgenie_alert_params.alert_exception_alias = alias

    summary = f'{endpoint} threw exception : {__exception_to_string(exception)} | Alert generated from {opsgenie_alert_params.alert_details["service_id"]}'
    description = f'{endpoint} has thrown exception : {__exception_to_string(exception)}. Complete URL : {url} called with method ' \
                    f'{method}. Endpoint served by service : {opsgenie_alert_params.alert_details["service_id"]} on host: ' \
                    f'{opsgenie_alert_params.alert_details["host"]}.'

    payload = {
        "message": summary,
        "description": description,
        "alias": opsgenie_alert_params.alert_exception_alias,
        "tags": opsgenie_alert_params.alert_tags,
        "details": opsgenie_alert_params.alert_details,
        "priority": opsgenie_alert_params.alert_priority.value,
    }

    # add responders if present
    if opsgenie_alert_params.alert_responder:
        payload["responders"] = opsgenie_alert_params.alert_responder

    # if traceback is not silenced then add traceback
    if not opsgenie_alert_params.no_traceback:
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            traceback_str = "".join(traceback.format_exception(exception))
        else:
            traceback_str = "".join(traceback.format_exception(etype=type(exception),
                                                               value=exception,
                                                               tb=exception.__traceback__))
        payload["description"] = f'{description} {traceback_str}'
        payload["details"]["Traceback"] = traceback_str

    # Now we are all set to make the alert api call to opsgenie
    try:
        make_opsgenie_api_request(
            http_verb="post", url=f'{opsgenie_alert_params.opsgenie_api_base}/v2/alerts', payload=payload,
            opsgenie_token=opsgenie_alert_params.opsgenie_token
        )
    except HTTPError as e:
        logger.exception(e)


def raise_manual_alert(exception:Exception=None, func_name:str=None, opsgenie_alert_params:OpsgenieAlertParams=None,
                       extra_props: Dict[str,str] = {}):

    if sys.version_info.major == 3 and sys.version_info.minor >= 10:
        trace_back = "".join(traceback.format_exception(exception))
    else:
        trace_back = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))

    exception_str = __exception_to_string(exception).replace(' ', '_')
    # add url info into details
    opsgenie_alert_params.alert_details["exception"] = __exception_to_string(exception)
    opsgenie_alert_params.alert_details["Traceback"] = trace_back

    # merge existing details dict with extra_props
    opsgenie_alert_params.alert_details = {**opsgenie_alert_params.alert_details, **extra_props}

    # update alias if not set
    # Alias: serviceid-funcname-exception-name-ALERT_ALIAS
    alias = f'{opsgenie_alert_params.alert_details["service_id"]}-{func_name}-{exception.__class__.__name__}-{opsgenie_alert_params.envtype}'
    if opsgenie_alert_params.alert_alias:
        opsgenie_alert_params.alert_alias = alias + "-" + opsgenie_alert_params.alert_alias
    else:
        opsgenie_alert_params.alert_alias = alias

    summary = f'{func_name} threw exception : {exception_str} | Alert generated from {opsgenie_alert_params.alert_details["service_id"]}'
    description = f'{func_name} has thrown exception : {exception_str}. Complete stack trace : {trace_back}'

    payload = {
        "message": summary,
        "description": description,
        "alias": opsgenie_alert_params.alert_alias,
        "tags": opsgenie_alert_params.alert_tags,
        "details": opsgenie_alert_params.alert_details,
        "priority": opsgenie_alert_params.alert_priority.value,
    }

    # add responders if present
    if opsgenie_alert_params.alert_responder:
        payload["responders"] = opsgenie_alert_params.alert_responder

    # Now we are all set to make the alert api call to opsgenie
    try:
        make_opsgenie_api_request(
            http_verb="post", url=f'{opsgenie_alert_params.opsgenie_api_base}/v2/alerts', payload=payload,
            opsgenie_token=opsgenie_alert_params.opsgenie_token
        )
    except Exception as e:
        logger.exception(e)



def raise_opsgenie_alert(alert_type:AlertType = None, alert_status_code:Optional[int] = None, \
                         alert_status_class:Optional[str] = None, elapsed_time:Optional[int] = None,
                         exception=None, opsgenie_alert_params:OpsgenieAlertParams=None, response_status_code: int=None,
                         func_name:str=None, extra_props: Dict[str,str] = {}, alert_priority: str = ''):

    # handle overrides
    if alert_priority != '':
        try:
            opsgenie_alert_params.alert_priority = AlertPriority(alert_priority)
        except ValueError as e:
            logger.exception(e)

    if alert_type == AlertType.STATUS_ALERT:
        if alert_status_code:
            raise_opsgenie_status_alert(alert_status_code=alert_status_code, opsgenie_alert_params=opsgenie_alert_params,
                                        response_status_code=response_status_code, extra_props=extra_props)
        elif alert_status_class:
            raise_opsgenie_status_alert(alert_status_class=alert_status_class, opsgenie_alert_params=opsgenie_alert_params,
                                        response_status_code=response_status_code, extra_props=extra_props)

    if alert_type == AlertType.LATENCY_ALERT:
        raise_opsgenie_latency_alert(elapsed_time=elapsed_time, alert_status_code=alert_status_code,
                                     opsgenie_alert_params=opsgenie_alert_params, extra_props=extra_props)

    if alert_type == AlertType.EXCEPTION:
        raise_opsgenie_exception_alert(exception=exception, opsgenie_alert_params=opsgenie_alert_params,
                                       extra_props=extra_props)

    if alert_type == AlertType.MANUAL:
        raise_manual_alert(exception=exception, func_name=func_name, opsgenie_alert_params=opsgenie_alert_params,
                           extra_props=extra_props)

