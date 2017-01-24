#!/bin/bash

. $(dirname $0)/../../include.rc
. $(dirname $0)/../../volume.rc
. $(dirname $0)/../../tier.rc
. $(dirname $0)/../../cluster.rc


# Creates a tiered volume with pure distribute hot and cold tiers
# Both hot and cold tiers will have an equal number of bricks.

function check_peers {
    $CLI_1 peer status | grep 'Peer in Cluster (Connected)' | wc -l
}

function create_dist_tier_vol () {
        TEST $CLI_1 volume create $V0 $H1:$B1/${V0} $H2:$B2/${V0} $H3:$B3/${V0}
        TEST $CLI_1 volume start $V0
        TEST $CLI_1 volume attach-tier $V0 $H1:$B1/${V0}_h1 $H2:$B2/${V0}_h2 $H3:$B3/${V0}_h3
}

function tier_daemon_status {
        local _VAR=CLI_$1
	echo $_VAR > /dev/tty
        local x=$(${!_VAR} volume status $V0 | grep 'Tier Daemon on localhost')
        echo $x > /dev/tty
        echo $x | awk '{print $7}'
}

cleanup;

#setup cluster and test volume
TEST launch_cluster 3; # start 3-node virtual cluster
TEST $CLI_1 peer probe $H2; # peer probe server 2 from server 1 cli
TEST $CLI_1 peer probe $H3; # peer probe server 3 from server 1 cli

EXPECT_WITHIN $PROBE_TIMEOUT 2 check_peers;

#Create and start a tiered volume
create_dist_tier_vol

#Issue detach tier on the tiered volume
#Will throw error saying detach tier not started

EXPECT "Tier command failed" $CLI_1 volume tier $V0 detach status

#after starting detach tier the detach tier status should display the status

TEST $CLI_1 volume tier $V0 detach start

EXPECT_WITHIN $PROCESS_UP_TIMEOUT "1" tier_detach_status

#kill a node
TEST kill_node 2

#check if we have the rest of the node available printed in the output of detach status
EXPECT_WITHIN $PROCESS_UP_TIMEOUT "1" tier_detach_status_node_down

#check if we have the rest of the node available printed in the output of tier status
EXPECT_WITHIN $PROCESS_UP_TIMEOUT "1" tier_status_node_down

TEST $glusterd_2;

EXPECT_WITHIN $PROBE_TIMEOUT 2 check_peers;
# Make sure we check that the *bricks* are up and not just the node.  >:-(
EXPECT_WITHIN $CHILD_UP_TIMEOUT 1 brick_up_status_1 $V0 $H2 $B2/${V0}
EXPECT_WITHIN $CHILD_UP_TIMEOUT 1 brick_up_status_1 $V0 $H2 $B2/${V0}_h2
EXPECT_WITHIN $PROCESS_UP_TIMEOUT Y tier_daemon_status 2

EXPECT_WITHIN $PROCESS_UP_TIMEOUT "1" tier_detach_status

TEST $CLI_1 volume tier $V0 detach stop

#If detach tier is stopped the detach tier command will fail

EXPECT "Tier command failed" $CLI_1 volume tier $V0 detach status

TEST $CLI_1 volume tier $V0 detach start

#wait for the detach to complete
EXPECT_WITHIN $PROCESS_UP_TIMEOUT "1" tier_detach_commit

#If detach tier is committed then the detach status should fail throwing an error
#saying its not a tiered volume

EXPECT "Tier command failed" $CLI_1 volume tier $V0 detach status

cleanup;

#G_TESTDEF_TEST_STATUS_NETBSD7=KNOWN_ISSUE,BUG=000000
