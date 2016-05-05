/*
  Copyright (c) 2016 Red Hat, Inc. <http://www.redhat.com>
  This file is part of GlusterFS.

  This file is licensed to you under your choice of the GNU Lesser
  General Public License, version 3 or any later version (LGPLv3 or
  later), or the GNU General Public License, version 2 (GPLv2), in all
  cases as published by the Free Software Foundation.
*/

#ifndef __EVENTTYPES_H__
#define __EVENTTYPES_H__

typedef enum {
    EVENT_SEND_OK,
    EVENT_ERROR_INVALID_INPUTS,
    EVENT_ERROR_SOCKET,
    EVENT_ERROR_CONNECT,
    EVENT_ERROR_SEND,
} event_errors_t;

typedef enum {
    EVENT_PEER_ATTACH,
    EVENT_PEER_DETACH,
    EVENT_VOLUME_CREATE,
    EVENT_VOLUME_START,
    EVENT_VOLUME_STOP,
    EVENT_VOLUME_SET,
    EVENT_VOLUME_RESET,
    EVENT_VOLUME_DELETE,
    EVENT_BRICKS_ADD,
    EVENT_BRICKS_REMOVE_START,
    EVENT_BRICKS_REMOVE_COMMIT,
    EVENT_BRICKS_REPLACE,
    EVENT_REBALANCE_START,
    EVENT_REBALANCE_STOP,
    EVENT_QUOTA_ENABLE,
    EVENT_QUOTA_DISABLE,
    EVENT_QUOTA_SET,
    EVENT_SELF_HEAL_ENABLE,
    EVENT_SELF_HEAL_DISABLE,
    EVENT_GEOREP_CREATE,
    EVENT_GEOREP_START,
    EVENT_GEOREP_CONFIG_SET,
    EVENT_GEOREP_CONFIG_RESET,
    EVENT_GEOREP_STOP,
    EVENT_GEOREP_DELETE,
    EVENT_GEOREP_PAUSE,
    EVENT_GEOREP_RESUME,
    EVENT_BITROT_ENABLE,
    EVENT_BITROT_DISABLE,
    EVENT_BITROT_CONFIG_SET,
    EVENT_BITROT_CONFIG_RESET,
    EVENT_SHARDING_ENABLE,
    EVENT_SHARDING_DISABLE,
    EVENT_SHARDING_CONFIG_SET,
    EVENT_SHARDING_CONFIG_RESET,
    EVENT_SNAPSHOT_CREATE,
    EVENT_SNAPSHOT_CLONE,
    EVENT_SNAPSHOT_RESTORE,
    EVENT_SNAPSHOT_CONFIG_SET,
    EVENT_SNAPSHOT_CONFIG_RESET,
    EVENT_SNAPSHOT_DELETE,
    EVENT_SNAPSHOT_ACTIVATE,
    EVENT_SNAPSHOT_DEACTIVATE,
    EVENT_LAST
} eventtypes_t;

#endif /* __EVENTTYPES_H__ */
