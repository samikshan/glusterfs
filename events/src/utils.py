# -*- coding: utf-8 -*-
import json
import os
import logging
import xml.etree.cElementTree as etree

import requests
from eventsapiconf import LOG_FILE, WEBHOOKS_FILE, \
    DEFAULT_CONFIG_FILE, CUSTOM_CONFIG_FILE
import eventtypes

from gluster.cliutils import execute

# Webhooks list
_webhooks = {}
# Default Log Level
_log_level = "INFO"
# Config Object
_config = {}
cache_data = {}

# Init Logger instance
logger = logging.getLogger(__name__)


def cache_output(func):
    def wrapper(*args, **kwargs):
        global cache_data
        if cache_data.get(func.func_name, None) is None:
            cache_data[func.func_name] = func(*args, **kwargs)

        return cache_data[func.func_name]
    return wrapper


def get_event_type_name(idx):
    """
    Returns Event Type text from the index. For example, VOLUME_CREATE
    """
    return eventtypes.all_events[idx].replace("EVENT_", "")


def setup_logger():
    """
    Logging initialization, Log level by default will be INFO, once config
    file is read, respective log_level will be set.
    """
    global logger
    logger.setLevel(logging.INFO)

    # create the logging file handler
    fh = logging.FileHandler(LOG_FILE)

    formatter = logging.Formatter("[%(asctime)s] %(levelname)s "
                                  "[%(module)s - %(lineno)s:%(funcName)s] "
                                  "- %(message)s")

    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)


def load_config():
    """
    Load/Reload the config from REST Config files. This function will
    be triggered during init and when SIGUSR2.
    """
    global _config
    _config = {}
    if os.path.exists(DEFAULT_CONFIG_FILE):
        _config = json.load(open(DEFAULT_CONFIG_FILE))
    if os.path.exists(CUSTOM_CONFIG_FILE):
        _config.update(json.load(open(CUSTOM_CONFIG_FILE)))


def load_log_level():
    """
    Reads log_level from Config file and sets accordingly. This function will
    be triggered during init and when SIGUSR2.
    """
    global logger, _log_level
    new_log_level = _config.get("log_level", "INFO")
    if _log_level != new_log_level:
        logger.setLevel(getattr(logging, new_log_level.upper()))
        _log_level = new_log_level.upper()


def load_webhooks():
    """
    Load/Reload the webhooks list. This function will
    be triggered during init and when SIGUSR2.
    """
    global _webhooks
    _webhooks = {}
    if os.path.exists(WEBHOOKS_FILE):
        _webhooks = json.load(open(WEBHOOKS_FILE))


def load_all():
    """
    Wrapper function to call all load/reload functions. This function will
    be triggered during init and when SIGUSR2.
    """
    load_webhooks()
    load_log_level()


@cache_output
def get_my_uuid():
    cmd = ["gluster", "system::", "uuid", "get", "--xml"]
    rc, out, err = execute(cmd)

    if rc != 0:
        return None

    tree = etree.fromstring(out)
    uuid_el = tree.find("uuidGenerate/uuid")
    return uuid_el.text


def publish(ts, event_key, data):
    message = {
        "nodeid": get_my_uuid(),
        "ts": int(ts),
        "event": get_event_type_name(event_key),
        "message": data
    }
    if _webhooks:
        plugin_webhook(message)
    else:
        # TODO: Defaul action?
        pass


def plugin_webhook(message):
    message_json = json.dumps(message, sort_keys=True)
    logger.debug("EVENT: {0}".format(message_json))
    for url, token in _webhooks.items():
        http_headers = {"Content-Type": "application/json"}
        if token != "" and token is not None:
            http_headers["Authorization"] = "Bearer " + token

        try:
            resp = requests.post(url, headers=http_headers, data=message_json)
        except requests.ConnectionError as e:
            logger.warn("Event push failed to URL: {url}, "
                        "Event: {event}, "
                        "Status: {error}".format(
                            url=url,
                            event=message_json,
                            error=e))
            continue

        if resp.status_code != 200:
            logger.warn("Event push failed to URL: {url}, "
                        "Event: {event}, "
                        "Status Code: {status_code}".format(
                            url=url,
                            event=message_json,
                            status_code=resp.status_code))
