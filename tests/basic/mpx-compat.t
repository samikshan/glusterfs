#!/bin/bash
#This test tests that self-heals don't perform fsync when durability is turned
#off

. $(dirname $0)/../include.rc
. $(dirname $0)/../volume.rc

function count_processes {
	# -x means exact, so we don't get glusterd, glusterfs, etc.
	pgrep -x glusterfsd | wc -w
}

export MULTIPLEX=1

TEST glusterd

# Create two vanilla volumes.
TEST $CLI volume create $V0 $H0:$B0/brick-${V0}-{0,1}
TEST $CLI volume create $V1 $H0:$B0/brick-${V1}-{0,1}

# Start both.
TEST $CLI volume start $V0
TEST $CLI volume start $V1

# There should be only one process for compatible volumes.
EXPECT 1 count_processes

# Make the second volume incompatible with the first.
TEST $CLI volume stop $V1
TEST $CLI volume set $V1 server.manage-gids no
TEST $CLI volume start $V1

# There should be two processes this time (can't share protocol/server).
EXPECT 2 count_processes

cleanup
