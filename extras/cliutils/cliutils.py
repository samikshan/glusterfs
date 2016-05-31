# -*- coding: utf-8 -*-
from __future__ import print_function
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import inspect
import subprocess
import os
import xml.etree.cElementTree as etree
import json
import sys

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                        description=__doc__)
subparsers = parser.add_subparsers(dest="mode")

subcommands = {}
cache_data = {}
ParseError = etree.ParseError if hasattr(etree, 'ParseError') else SyntaxError


class GlusterCmdException(Exception):
    pass


def cache_output(func):
    # Decorator func can cache the output of any function. If a
    # function is executed twice then returns cached output for
    # second time.
    def wrapper(*args, **kwargs):
        global cache_data
        if cache_data.get(func.func_name, None) is None:
            cache_data[func.func_name] = func(*args, **kwargs)

        return cache_data[func.func_name]
    return wrapper


@cache_output
def get_node_uuid():
    cmd = ["gluster", "system::", "uuid", "get", "--xml"]
    rc, out, err = execute(cmd)

    if rc != 0:
        return None

    tree = etree.fromstring(out)
    uuid_el = tree.find("uuidGenerate/uuid")
    return uuid_el.text


def yesno(flag):
    return "Yes" if flag else "No"


def oknotok(flag):
    return "OK" if flag else "NOT OK"


def output_error(message):
    print (message, file=sys.stderr)
    sys.exit(1)


def node_output_ok(message=""):
    # Prints Success JSON output and exits with returncode zero
    out = {"ok": True, "nodeid": get_node_uuid(), "output": message}
    print (json.dumps(out))
    sys.exit(0)


def node_output_notok(message):
    # Prints Error JSON output and exits with returncode zero
    out = {"ok": False, "nodeid": get_node_uuid(), "error": message}
    print (json.dumps(out))
    sys.exit(0)


def execute(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out, err


def get_pool_list():
    cmd = ["gluster", "--mode=script", "pool", "list", "--xml"]
    rc, out, err = execute(cmd)
    tree = etree.fromstring(out)

    pool = []
    try:
        for p in tree.findall('peerStatus/peer'):
            pool.append({"nodeid": p.find("uuid").text,
                         "hostname": p.find("hostname").text,
                         "connected": (True if p.find("connected").text == "1"
                                       else False)})
    except (ParseError, AttributeError, ValueError) as e:
        output_error("Failed to parse Pool Info: {0}".format(e))

    return pool


class NodeOutput(object):
    def __init__(self, **kwargs):
        self.nodeid = kwargs.get("nodeid", "")
        self.hostname = kwargs.get("hostname", "")
        self.node_up = kwargs.get("node_up", False)
        self.ok = kwargs.get("ok", False)
        self.output = kwargs.get("output", "N/A")
        self.error = kwargs.get("error", "N/A")


def execute_in_peers(name, args=[]):
    # Get the file name of Caller function, If the file name is peer_example.py
    # then Gluster peer command will be gluster system:: execute example.py
    # Command name is without peer_
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    actual_file = module.__file__
    # If file is symlink then find actual file
    if os.path.islink(actual_file):
        actual_file = os.readlink(actual_file)

    # Get the name of file without peer_
    cmd_name = os.path.basename(actual_file).replace("peer_", "")
    cmd = ["gluster", "system::", "execute", cmd_name, name] + args
    rc, out, err = execute(cmd)
    if rc != 0:
        raise GlusterCmdException((rc, out, err, " ".join(cmd)))

    out = out.strip().splitlines()

    # JSON decode each line and construct one object with node id as key
    all_nodes_data = {}
    for node_data in out:
        data = json.loads(node_data)
        all_nodes_data[data["nodeid"]] = {
            "nodeid": data.get("nodeid"),
            "ok": data.get("ok"),
            "output": data.get("output", ""),
            "error": data.get("error", "")}

    # gluster pool list
    pool_list = get_pool_list()

    data_out = []
    # Iterate pool_list and merge all_nodes_data collected above
    # If a peer node is down then set node_up = False
    for p in pool_list:
        p_data = all_nodes_data.get(p.get("nodeid"), None)
        row_data = NodeOutput(node_up=False,
                              hostname=p.get("hostname"),
                              nodeid=p.get("nodeid"),
                              ok=False)

        if p_data is not None:
            # Node is UP
            row_data.node_up = True
            row_data.ok = p_data.get("ok")
            row_data.output = p_data.get("output")
            row_data.error = p_data.get("error")

        data_out.append(row_data)

    return data_out


def sync_file_to_peers(fname):
    # Copy file from current node to all peer nodes, fname
    # is path after GLUSTERD_WORKDIR
    cmd = ["gluster", "system::", "copy", "file", fname]
    rc, out, err = execute(cmd)
    if rc != 0:
        raise GlusterCmdException((rc, out, err))


class Cmd(object):
    name = ""

    def run(self, args):
        # Must required method. Raise NotImplementedError if derived class
        # not implemented this method
        raise NotImplementedError("\"run(self, args)\" method is "
                                  "not implemented by \"{0}\"".format(
                                      self.__class__.__name__))


def runcli():
    # Get list of Classes derived from class "Cmd" and create
    # a subcommand as specified in the Class name. Call the args
    # method by passing subcommand parser, Derived class can add
    # arguments to the subcommand parser.
    for c in Cmd.__subclasses__():
        cls = c()
        if getattr(cls, "name", "") == "":
            raise NotImplementedError("\"name\" is not added "
                                      "to \"{0}\"".format(
                                          cls.__class__.__name__))

        p = subparsers.add_parser(cls.name)
        args_func = getattr(cls, "args", None)
        if args_func is not None:
            args_func(p)

        # A dict to save subcommands, key is name of the subcommand
        subcommands[cls.name] = cls

    # Get all parsed arguments
    args = parser.parse_args()

    # Get the subcommand to execute
    cls = subcommands.get(args.mode, None)

    # Run
    if cls is not None:
        cls.run(args)
