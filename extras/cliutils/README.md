# CLI utility for creating Cluster aware CLI tools for Gluster
Python library `cliutils` provides wrapper around `gluster system::
execute` CLI to create Cluster aware CLI utilities to extend the
functionalities of Gluster.

Example use cases:
- Start a service in all peer nodes of Cluster
- Collect the status of a service from all peer nodes
- Collect the config values from each peer nodes and display latest
  config based on version.
- Copy a file present in GLUSTERD_WORKDIR from one peer node to all
  other peer nodes.(Geo-replication create push-pem is using this to
  distribute the SSH public keys from all master nodes to all slave
  nodes)
- Generate pem keys in all peer nodes and collect all the public keys
  to one place(Geo-replication gsec_create is doing this)
- Provide Config sync CLIs for new features like `gluster-eventsapi`,
  `gluster-restapi`, `gluster-mountbroker` etc.

## Introduction

Gluster has a hidden gem to run command in specific node or in all
nodes using `gluster system:: execute` command, This command is mainly
used by Geo-replication(gsec_create and mountbroker) but it can be
used for other purposes also.

Create a executable file with filename starting with `peer_` under
$GLUSTER_LIBEXEC directory.

Example, Create a file `/usr/libexec/glusterfs/peer_hello` and make
the file executable

    #!/usr/bin/env bash
    echo "Hello from $(gluster system:: uuid get)"

Now run,

    gluster system:: execute hello

It will run `peer_hello` executable in all peer nodes and shows the
output from each node(Below example shows output from my two nodes
cluster)

    Hello from UUID: e7a3c5c8-e7ad-47ad-aa9c-c13907c4da84
    Hello from UUID: c680fc0a-01f9-4c93-a062-df91cc02e40f

If we need to run a command specifically on one of the peer, then we
can send node UUID as parameter so that we can handle that in our
script.

    #!/usr/bin/env bash
    nodeuuid=$(gluster system:: uuid get | sed 's/UUID: //')
    if test "x$nodeuuid" = "x$1" || test "x$1" = "x"; then
        echo "Hello from $nodeuuid"
    fi

If we call `gluster system:: execute hello` without UUID parameter
then it runs in all peer nodes, if we specify a UUID then we can run
only in that node. For example,

    gluster system:: execute hello e7a3c5c8-e7ad-47ad-aa9c-c13907c4da84

Interesting?

We have couple of issues to use `system:: execute` commands directly,

- If a node is down in the cluster, `system:: execute` just skips it
  and runs only in up nodes.
- `system:: execute` commands are not user friendly
- It captures only stdout, so handling errors is tricky.

## cliutils

Introducing a framework in Python for creating cluster aware cli tools
for Gluster!

**Advantages:**

- Single executable file will act as node component as well as User CLI.
- `execute_in_peers` utility function will merge the `gluster system::
  execute` output with `gluster peer status` to identify offline nodes.
- Easy CLI Arguments handling.
- Extra CLI utilities like CliTable, colored output etc.
- If node component returns non zero return value then, `gluster
  system:: execute` will fail to aggregate the output from other
  nodes. `node_output_ok` or `node_output_notok` utility functions
  returns zero both in case of success or error, but returns json
  with ok: true or ok:false respectively.
- Easy to iterate on the node outputs.
- Better error handling - Geo-rep CLIs `gluster system:: execute
  mountbroker`, `gluster system:: execute gsec_create` and `gluster
  system:: add_secret_pub` are suffering from error handling. These
  tools are notifying user if any failures during execute or if a node
  is down during execute.

### Hello World
Create a file called `message.py`

    #!/usr/bin/env python
    from cliutils import Cmd, runcli

    class Hello(Cmd):
        name = "hello"

        def args(self, parser):
            parser.add_argument("--msg", default="World!")

        def run(self, args):
            print ("Hello, %s" % args.msg)

    if __name__ == "__main__":
        runcli()

This can now be called as `python message.py hello` or `python
message.py hello --msg`

Nothing special in the above command, executes in single node and prints the
output. If we need to create a command which runs in all peer nodes of
Gluster Cluster then,

Create a file in `$LIBEXEC/glusterfs/peer_message.py` with following
content. Please note file name should start with `peer_` to use it
with `gluster system:: execute` infrastructure.

    #!/usr/bin/env python
    from cliutils import Cmd, runcli, execute_in_peers, node_output_ok

    class NodeHello(Cmd):
        name = "node-hello"

        def run(self, args):
            node_output_ok("Hello")

    class Hello(Cmd):
        name = "hello"

        def run(self, args):
            out = execute_in_peers("node-hello")
            for row in out:
                print ("{0} from {1}".format(row.output, row.hostname))

    if __name__ == "__main__":
        runcli()

When we run `python peer_message.py`, it will have two subcommands,
"node-hello" and "hello". This file should be copied to
`$LIBEXEC/glusterfs` directory in all peer nodes. User will call
subcommand "hello" from any one peer node, which internally call
`gluster system:: execute message.py node-hello`(This runs in all peer
nodes and collect the outputs)

For node component, do not print the output directly use
`node_output_ok` or `node_output_notok` functions. `node_output_ok`
additionally collect the node UUID and prints in JSON
format. `execute_in_peers` function will collect this output and
merges with `peers list` so that we don't miss the node information if
that node is offline.

If you observed already, function `args` is optional, if you don't
have arguments then no need to create a function. When we run the
file, we will have two subcommands. For example,

    python peer_message.py hello
    python peer_message.py node-hello

First subcommand calls second subcommand in all peer nodes. Basically
`execute_in_peers(NAME, ARGS)` will be converted into

    cmd_name = FILENAME without "peers_"
    gluster system:: execute <CMD_NAME> <SUBCOMMAND> <ARGS>

In our example,

    filename = "peer_message.py"
    cmd_name = "message.py"
    gluster system:: execute message.py node-hello

**Note**: `peer_message.py` should be executable file and should be present
in `$LIBEXEC/glusterfs` directory(Ex: `/usr/local/libexec/glusterfs/`)

Now create symlink to `/usr/bin` or `/usr/sbin` directory depending on
the usecase.

    ln -s /usr/libexec/glusterfs/peer_message.py /usr/bin/gluster-message

Now users will use `gluster-message` instead of using system:: execute
commands.

    gluster-message hello

### Showing CLI output as Table

    #!/usr/bin/env python
    from cliutils import (Cmd, runcli, CliTable, execute_in_peers,
                                  node_output_ok)

    class NodeHello(Cmd):
        name = "node-hello"

        def run(self, args):
            node_output_ok("Hello")

    class Hello(Cmd):
        name = "hello"

        def run(self, args):
            out = execute_in_peers("node-hello")
            # Initialize the CLI table
            table = CliTable(num_columns=4)
            table.add_title_row("ID", "NODE", "NODE STATUS", "MESSAGE")
            for row in out:
                table.add_row(row.nodeid,
                              row.hostname,
                              "UP" if row.node_up else "DOWN",
                              row.output if row.ok else row.error)

            table.display()

    if __name__ == "__main__":
        runcli()


Example output,

    ID                                     NODE        NODE STATUS   MESSAGE
    ------------------------------------------------------------------------
    e7a3c5c8-e7ad-47ad-aa9c-c13907c4da84   localhost   UP            Hello
    bb57a4c4-86eb-4af5-865d-932148c2759b   vm2         UP            Hello
    f69b918f-1ffa-4fe5-b554-ee10f051294e   vm3         DOWN          N/A

### CLI Table
In the above example, CliTable is used. CliTable is a utility class
which can be used for creating autowidth tables in CLI output. It is
also possible to create colored output.

    #!/usr/bin/env python
    from cliutils import CliTable

    data = [{"node": "vm1", "status": "UP"},
            {"node": "vm2", "status": "DOWN"}]

    # Example1: Without color
    table1 = CliTable(num_columns=2)
    table1.add_title_row("NODE", "STATUS")

    for row in data:
        table1.add_row(row["node"], row["status"])

    print ("\nExample 1: Without Color")
    table1.display()

    # Example2: With colored values
    def color_status(value):
        if value == "UP":
            return "green"
        else:
            return "red"

    table2 = CliTable(num_columns=2)
    table2.add_title_row("NODE", "STATUS")

    # Format second column to show the color, color_status is
    # a func defined above
    table2.format_column(2, color=color_status, align="right")

    for row in data:
        table2.add_row(row["node"], row["status"])

    print ("Example 2: With Color")
    table2.display()

    # Example3: Row Color
    def color_status_row(cols):
        # cols is array of row values, cols[1] is status
        if cols[1] == "UP":
            return "green"
        else:
            return "red"

    table3 = CliTable(num_columns=2, row_color_func=color_status_row)
    table3.add_title_row("NODE", "STATUS")

    for row in data:
        table3.add_row(row["node"], row["status"])

    print ("Example 3: With row Color")
    table3.display()

## How to package in Gluster
If the project is created in `$GLUSTER_SRC/tools/message`

Add "message" to SUBDIRS list in `$GLUSTER_SRC/tools/Makefile.am`

and then create a `Makefile.am` in `$GLUSTER_SRC/tools/message`
directory with following content.

    EXTRA_DIST = peer_message.py

    peertoolsdir = $(libexecdir)/glusterfs/
    peertools_SCRIPTS = peer_message.py

    install-exec-hook:
        $(mkdir_p) $(DESTDIR)$(bindir)
        rm -f $(DESTDIR)$(bindir)/gluster-message
        ln -s $(libexecdir)/glusterfs/peer_message.py \
            $(DESTDIR)$(bindir)/gluster-message

    uninstall-hook:
        rm -f $(DESTDIR)$(bindir)/gluster-message

Thats all. Add following files in `glusterfs.spec.in` if packaging is
required.(Under `%files` section)

    %{_libexecdir}/glusterfs/peer_message.py*
    %{_bindir}/gluster-message

## Who is using cliutils
- gluster-mountbroker   http://review.gluster.org/14544
- gluster-eventsapi     http://review.gluster.org/14248
- gluster-georep-sshkey http://review.gluster.org/14732
- gluster-restapi       https://github.com/aravindavk/glusterfs-restapi

## Limitations/TODOs
- Not yet possible to create CLI without any subcommand, For example
  `gluster-message` without any arguments
- Hiding node subcommands in `--help`(`gluster-message --help` will
  show all subcommands including node subcommands)
- Only positional arguments supported for node arguments, Optional
  arguments can be used for other commands.
- JSON support for CliTable, `table.display(json=True)` can emit JSON
  output.
