#!/usr/bin/env python

# imports
import argparse
import errno
import gpiozero
import os
import sys
import time


# constants
#   node names
#   edit as needed
P1_NAME = 'p1.local'
P2_NAME = 'p2.local'
P3_NAME = 'p3.local'
P4_NAME = 'p4.local'
#   power control pins (BCM numbering)
P1_PIN = 6
P2_PIN = 13
P3_PIN = 19
P4_PIN = 26
#   led (BCM numbering)
LED_PIN = 5
#   UIDs
LOCAL_UNAME = 'pi'
ROOT_UID = 0
#   commands
REMOTE_OFF = 'su ' + LOCAL_UNAME + ' -c "ssh -qn %s \\\"sudo poweroff\\\" &"'
#   node parameters
NODE_DELAY = 5
NODE_PING_INTERVAL = 1
#   indices for node data
NODE_PIN = 0
NODE_NAME = 1
NODE_PINGER = 2
#   gpio path
GPIO_PATH = '/sys/class/gpio/gpio%s/value'

# gobals
exit_code = 0


# function definitions
def power_off(pin):
    global exit_code
    try:
        with open(GPIO_PATH % pin, 'w') as p:
            p.write('0')
    except IOError:
        exit_code = errno.EIO
        sys.stderr.write('Power off failed: Unable to access gpio %s\n' % pin)

def power_on(pin):
    global exit_code
    try:
        with open(GPIO_PATH % pin, 'w') as p:
            p.write('1')
    except IOError:
        exit_code = errno.EIO
        sys.stderr.write('Power on failed: Unable to access gpio %s\n' % pin)

def power_state(pin):
    try:
        with open(GPIO_PATH % pin, 'r') as p:
            return int(p.read(1))
    except IOError:
            return -1

def do_stop():
    for k in sorted(nodes):
        if power_state(nodes[k][NODE_PIN]) != 0:
            if args.hard == False:
                if args.verbose:
                    print 'Sending shutdown command to %s' % nodes[k][NODE_NAME]
                os.system(REMOTE_OFF % nodes[k][NODE_NAME])
                while nodes[k][NODE_PINGER].value == 1:
                    time.sleep(NODE_PING_INTERVAL)
                time.sleep(NODE_DELAY)
            if args.verbose:
                print 'Powering off %s' % nodes[k][NODE_NAME]
            power_off(nodes[k][NODE_PIN])
        elif args.verbose:
            print nodes[k][NODE_NAME], 'is already off.'

def do_start():
    for k in sorted(nodes):
        if args.verbose:
            print 'Powering on', nodes[k][NODE_NAME]
        power_on(nodes[k][NODE_PIN])
        if k != 'p4':
            time.sleep(NODE_DELAY)

def do_restart():
    do_stop()
    do_start()

def do_status():
    # get and display status of all nodes
    for k in sorted(nodes):
        status = nodes[k][NODE_NAME] + ': '
        p_state = power_state(nodes[k][NODE_PIN])
        if p_state != 0:
            pingable = nodes[k][NODE_PINGER].value
        if p_state == 0:
            status += 'Off.'
        else:
            if pingable:
                status += 'Up.'
                if args.verbose:
                    status += ' Responding to pings.'
            elif p_state == 1:
                status += 'On.'
                if args.verbose:
                    status += ' Not responding to pings.'
            else:
                status += 'Unknown.'
                if args.verbose:
                    status += ' Unable to read gpio state and not responding to pings.'
        print status


# do stuff
if __name__ == '__main__':
    if os.geteuid() != ROOT_UID:
        sys.stderr.write('Must be root.')
        sys.exit(errno.EACCESS)

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['stop', 'start', 'restart', 'status'])
    parser.add_argument('--hard', action='store_true', default=False,
                        help="don't attempt clean shutdown or restart. Just switch node power instead.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    if args.verbose:
        print "Working..."

    # turn on warning LED
    warn_led = gpiozero.LED(LED_PIN)
    warn_led.blink(on_time=0.5, off_time=0.5)

    
    nodes = {'p1':[P1_PIN, P1_NAME, None],
             'p2':[P2_PIN, P2_NAME, None],
             'p3':[P3_PIN, P3_NAME, None],
             'p4':[P4_PIN, P4_NAME, None]}

    # pingers
    if args.action in ['stop', 'restart', 'status']:
        for k in nodes:
            try:
                if power_state(nodes[k][NODE_PIN]) != 0:
                    nodes[k][NODE_PINGER] = gpiozero.PingServer(nodes[k][NODE_NAME])
            except GPIOZeroError:
                pass

    if args.action == 'status':
        do_status()
    elif args.action == 'stop':
        do_stop()
    elif args.action == 'start':
        do_start()
    elif args.action == 'restart':
        do_restart()

    # cleanup
    warn_led.close()
    for k in nodes:
        try:
            node[k][NODE_PINGER].close()
        except:
            pass

##    sys.exit(exit_code)
