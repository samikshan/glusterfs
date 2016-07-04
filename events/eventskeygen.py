#!/usr/bin/env python
import os

GLUSTER_SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
eventtypes_h = os.path.join(GLUSTER_SRC_ROOT, "libglusterfs/src/eventtypes.h")
eventtypes_py = os.path.join(GLUSTER_SRC_ROOT, "events/src/eventtypes.py")

cr_c = """/*
  Copyright (c) 2016 Red Hat, Inc. <http://www.redhat.com>
  This file is part of GlusterFS.

  This file is licensed to you under your choice of the GNU Lesser
  General Public License, version 3 or any later version (LGPLv3 or
  later), or the GNU General Public License, version 2 (GPLv2), in all
  cases as published by the Free Software Foundation.
*/"""

cr_py = """#
#  Copyright (c) 2016 Red Hat, Inc. <http://www.redhat.com>
#  This file is part of GlusterFS.
#
#  This file is licensed to you under your choice of the GNU Lesser
#  General Public License, version 3 or any later version (LGPLv3 or
#  later), or the GNU General Public License, version 2 (GPLv2), in all
#  cases as published by the Free Software Foundation.
#"""

# When adding new keys add it to the END
keys = (
    "EVENT_PEER_ATTACH",
    "EVENT_PEER_DETACH",

    "EVENT_VOLUME_CREATE",
    "EVENT_VOLUME_START",
    "EVENT_VOLUME_STOP",
    "EVENT_VOLUME_SET",
    "EVENT_VOLUME_RESET",
    "EVENT_VOLUME_DELETE",

    "EVENT_BRICKS_ADD",
    "EVENT_BRICKS_REMOVE_START",
    "EVENT_BRICKS_REMOVE_COMMIT",
    "EVENT_BRICKS_REPLACE",

    "EVENT_REBALANCE_START",
    "EVENT_REBALANCE_STOP",

    "EVENT_QUOTA_ENABLE",
    "EVENT_QUOTA_DISABLE",
    "EVENT_QUOTA_SET",

    "EVENT_SELF_HEAL_ENABLE",
    "EVENT_SELF_HEAL_DISABLE",

    "EVENT_GEOREP_CREATE",
    "EVENT_GEOREP_START",
    "EVENT_GEOREP_CONFIG_SET",
    "EVENT_GEOREP_CONFIG_RESET",
    "EVENT_GEOREP_STOP",
    "EVENT_GEOREP_DELETE",
    "EVENT_GEOREP_PAUSE",
    "EVENT_GEOREP_RESUME",

    "EVENT_BITROT_ENABLE",
    "EVENT_BITROT_DISABLE",
    "EVENT_BITROT_CONFIG_SET",
    "EVENT_BITROT_CONFIG_RESET",

    "EVENT_SHARDING_ENABLE",
    "EVENT_SHARDING_DISABLE",
    "EVENT_SHARDING_CONFIG_SET",
    "EVENT_SHARDING_CONFIG_RESET",

    "EVENT_SNAPSHOT_CREATE",
    "EVENT_SNAPSHOT_CLONE",
    "EVENT_SNAPSHOT_RESTORE",
    "EVENT_SNAPSHOT_CONFIG_SET",
    "EVENT_SNAPSHOT_CONFIG_RESET",
    "EVENT_SNAPSHOT_DELETE",
    "EVENT_SNAPSHOT_ACTIVATE",
    "EVENT_SNAPSHOT_DEACTIVATE"
)

LAST_EVENT = "EVENT_LAST"

ERRORS = (
    "EVENT_SEND_OK",
    "EVENT_ERROR_INVALID_INPUTS",
    "EVENT_ERROR_SOCKET",
    "EVENT_ERROR_CONNECT",
    "EVENT_ERROR_SEND"
)

# Generate eventtypes.h
with open(eventtypes_h, "w") as f:
    f.write("{0}\n\n".format(cr_c))
    f.write("#ifndef __EVENTTYPES_H__\n")
    f.write("#define __EVENTTYPES_H__\n\n")
    f.write("typedef enum {\n")
    for k in ERRORS:
        f.write("    {0},\n".format(k))
    f.write("} event_errors_t;\n")

    f.write("\n")

    f.write("typedef enum {\n")
    for k in keys:
        f.write("    {0},\n".format(k))

    f.write("    {0}\n".format(LAST_EVENT))
    f.write("} eventtypes_t;\n")
    f.write("\n#endif /* __EVENTTYPES_H__ */\n")

# Generate eventtypes.py
with open(eventtypes_py, "w") as f:
    f.write("# -*- coding: utf-8 -*-\n")
    f.write("{0}\n\n".format(cr_py))
    f.write("all_events = [\n")
    for ev in keys:
        f.write('    "{0}",\n'.format(ev))
    f.write("]\n")
