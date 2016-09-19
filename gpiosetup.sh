#!/bin/bash
# this will likely fail if not run as root
# sets up sysfs exports for clusterhat power and led pins
#
# run from rc.local, an @reboot cron job etc.
# BCM pin mumbering

# warning LED
echo 5 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio5/direction
# P1
echo 6 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio6/direction
# P2
echo 13 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio13/direction
# P3
echo 19 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio19/direction
# P4
#echo 26 > /sys/class/gpio/export
#echo out > /sys/class/gpio/gpio26/direction
