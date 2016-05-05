# -*- coding: utf-8 -*-
import utils


def generic_handler(ts, key, data):
    """
    Generic handler to broadcast message to all peers, custom handlers
    can be created by func name handler_<event_name>
    Ex: handle_event_volume_create(ts, key, data)
    """
    utils.publish(ts, key, data)
