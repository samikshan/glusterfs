#!/bin/bash

. $(dirname $0)/../../include.rc
. $(dirname $0)/../../volume.rc
. $(dirname $0)/../../fileio.rc

cleanup;

ODIR="/var/tmp/gdstates/"
NOEXDIR="/var/tmp/gdstatesfoo/"

function get_daemon_not_supported_part {
        echo $1
}

function get_usage_part {
        echo $7
}

function get_directory_doesnt_exist_part {
        echo $1
}

function get_parsing_arguments_part {
        echo $1
}

TEST glusterd
TEST pidof glusterd
TEST mkdir $ODIR

OPATH=$(echo `$CLI get-state` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

OPATH=$(echo `$CLI get-state glusterd` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

TEST ! $CLI get-state glusterfsd;
ERRSTR=$($CLI get-state glusterfsd 2>&1 >/dev/null);
EXPECT 'glusterd' get_daemon_not_supported_part $ERRSTR;
EXPECT 'Usage:' get_usage_part $ERRSTR;

OPATH=$(echo `$CLI get-state file gdstate` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

OPATH=$(echo `$CLI get-state glusterd file gdstate` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

TEST ! $CLI get-state glusterfsd file gdstate;
ERRSTR=$($CLI get-state glusterfsd file gdstate 2>&1 >/dev/null);
EXPECT 'glusterd' get_daemon_not_supported_part $ERRSTR;
EXPECT 'Usage:' get_usage_part $ERRSTR;

OPATH=$(echo `$CLI get-state odir $ODIR` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

OPATH=$(echo `$CLI get-state glusterd odir $ODIR` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

OPATH=$(echo `$CLI get-state odir $ODIR file gdstate` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

OPATH=$(echo `$CLI get-state glusterd odir $ODIR file gdstate` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

OPATH=$(echo `$CLI get-state glusterd odir $ODIR file gdstate` | awk '{print $5}' | tr -d '\n')
TEST fd=`fd_available`
TEST fd_open $fd "r" $OPATH;
TEST fd_close $fd;
rm $OPATH

TEST ! $CLI get-state glusterfsd odir $ODIR;
ERRSTR=$($CLI get-state glusterfsd odir $ODIR 2>&1 >/dev/null);
EXPECT 'glusterd' get_daemon_not_supported_part $ERRSTR;
EXPECT 'Usage:' get_usage_part $ERRSTR;

TEST ! $CLI get-state glusterfsd odir $ODIR file gdstate;
ERRSTR=$($CLI get-state glusterfsd odir $ODIR file gdstate 2>&1 >/dev/null);
EXPECT 'glusterd' get_daemon_not_supported_part $ERRSTR;
EXPECT 'Usage:' get_usage_part $ERRSTR;

TEST ! $CLI get-state glusterfsd odir $NOEXDIR file gdstate;
ERRSTR=$($CLI get-state glusterfsd odir $NOEXDIR file gdstate 2>&1 >/dev/null);
EXPECT 'glusterd' get_daemon_not_supported_part $ERRSTR;
EXPECT 'Usage:' get_usage_part $ERRSTR;

TEST ! $CLI get-state odir $NOEXDIR;
ERRSTR=$($CLI get-state odir $NOEXDIR 2>&1 >/dev/null);
EXPECT 'Failed' get_directory_doesnt_exist_part $ERRSTR;

TEST ! $CLI get-state odir $NOEXDIR file gdstate;
ERRSTR=$($CLI get-state odir $NOEXDIR 2>&1 >/dev/null);
EXPECT 'Failed' get_directory_doesnt_exist_part $ERRSTR;

TEST ! $CLI get-state foo bar;
ERRSTR=$($CLI get-state foo bar 2>&1 >/dev/null);
EXPECT 'glusterd' get_daemon_not_supported_part $ERRSTR;
EXPECT 'Usage:' get_usage_part $ERRSTR;

TEST ! $CLI get-state glusterd foo bar;
ERRSTR=$($CLI get-state glusterd foo bar 2>&1 >/dev/null);
EXPECT 'Problem' get_parsing_arguments_part $ERRSTR;

rm -Rf $ODIR
cleanup;

