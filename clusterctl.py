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
N1_NAME = 'p1.local'
N2_NAME = 'p2.local'
N3_NAME = 'p3.local'
N4_NAME = 'p4.local'
#   power control pins (BCM numbering)
N1_PIN = 6
N2_PIN = 13
N3_PIN = 19
N4_PIN = 26
#   led (BCM numbering)
LED_PIN = 5
#   UIDs
LOCAL_UNAME = 'pi'
ROOT_UID = 0
#   commands
REMOTE_CMD = 'ssh %s "%s"'
REMOTE_OFF = 'sudo poweroff'
#   node parameters
NODE_DELAY = 5
NODE_PING_INTERVAL = 1
#   indices for node data
NODE_PIN = 0
NODE_NAME = 1
NODE_PINGER = 2
#   gpio path
GPIO_PATH = '/sys/class/gpio/gpio%s/value'
#   shutdown timeout (seconds)
S_TIMEOUT = 5
#   terminal colours
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"
                

# gobals
exit_code = 0


# class definitions
class store_nodelist(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        node_list = []
        for v in values:
            for c in v:
                if c not in node_list:
                    node_list.append(c)
        setattr(namespace, self.dest, node_list)


# function definitions
def node_id(string):
    valid_node_ids = '1234'
    valid = True
    if len(string) == 0:
        valid = False
    else:
        for c in string:
            if c not in valid_node_ids:
                valid = False
                break
    if valid:
        return string
    else:
        raise argparse.ArgumentTypeError('"%s" is not a valid node list' % string)
    
def power_off(pin):
    global exit_code
    try:
        with open(GPIO_PATH % pin, 'w') as p:
            p.write('0')
    except IOError:
        exit_code = errno.EIO
        sys.stderr.write(RED + 'Power off failed: Unable to access gpio %s\n' % pin
                         + RESET)

def power_on(pin):
    global exit_code
    try:
        with open(GPIO_PATH % pin, 'w') as p:
            p.write('1')
    except IOError:
        exit_code = errno.EIO
        sys.stderr.write(RED + 'Power on failed: Unable to access gpio %s\n' % pin
                         + RESET)

def power_state(pin):
    try:
        with open(GPIO_PATH % pin, 'r') as p:
            return int(p.read(1))
    except IOError:
            return -1

def do_stop():
    global exit_code
    for k in args.nodes:
        failed = False
        if power_state(nodes[k][NODE_PIN]) != 0:
            if args.hard == False:
                cmd=REMOTE_OFF
                if args.verbose:
                    print 'Stopping node(s)'
                do_command(node_list=k, cmd=REMOTE_OFF, quiet=True)
                end_time = time.time() + S_TIMEOUT
                while nodes[k][NODE_PINGER].value == 1 \
                      and time.time() < end_time:
                    time.sleep(NODE_PING_INTERVAL)
                if nodes[k][NODE_PINGER].value == 1:
                    failed = True
                else:
                    time.sleep(NODE_DELAY)
            if failed:
                exit_code = errno.EAGAIN
                msg = 'Timeout while waiting for node %s' % k
                if args.verbose:
                    msg += '(%s)' % nodes[k][NODE_NAME]
                msg +=' to shutdown.\nPower left on. Try "--hard" to force poweroff.\n' 
                sys.stderr.write(RED + msg + RESET)
            else:
                if args.verbose:
                    print 'Powering off %s' % nodes[k][NODE_NAME]
                power_off(nodes[k][NODE_PIN])
        elif args.verbose:
            print 'Node %s(%s)is already off.' % (k, nodes[k][NODE_NAME])

def do_start():
    for k in args.nodes:
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
    for k in args.nodes:
        status = 'Node '+ k
        if args.verbose:
            status += '(' + nodes[k][NODE_NAME] + ')'
        status += ': '
        p_state = power_state(nodes[k][NODE_PIN])
        if p_state != 0:
            if args.hard:
                pingable = 0
            else:
                pingable = nodes[k][NODE_PINGER].value
        if p_state == 0:
            status += 'Off.'
        else:
            if pingable:
                status += 'Up.'
                if args.verbose and args.hard != True:
                    status += ' Responding to pings.'
            elif p_state == 1:
                status += 'On.'
                if args.verbose and args.hard != True:
                    status += ' Not responding to pings.'
            else:
                status += 'Unknown.'
                if args.verbose and args.hard != True:
                    status += ' Unable to read gpio state and not responding to pings.'
        print status

def do_command(node_list=None, cmd=None, quiet=False):
    if node_list is None:
        node_list = args.nodes
    if cmd is None:
        cmd = args.command
    for k in node_list:
        header = 'Node ' + k
        if args.verbose:
            header += '(' + nodes[k][NODE_NAME] + ')'
        print header
        run_cmd = REMOTE_CMD % (nodes[k][NODE_NAME], cmd)
        if quiet:
            run_cmd += ' >/dev/null 2>&1'
        os.system(run_cmd)

        
# do stuff
if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description='Perform action on nodes attached to a clusterhet.')
    parser.add_argument('--hard', action='store_true', 
                        help=("don't attempt clean shutdown or restart. "
                              "Just switch node power instead. "
                              "Report only power state, "
                              "don't attempt to check whether server is responsive."))
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-n', '--nodes', nargs=1, default=['1','2','3','4'],
                        action=store_nodelist, type=node_id,
                        help=('List of nodes to target e.g. 123.'
                              ' Action is applied to all nodes when not present.'))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('action', choices=['stop', 'start', 'restart', 'status'],
                           nargs='?', help='action to be performed.')
    group.add_argument('-c', dest='command', metavar='COMMAND',
                        help=('run "COMMAND" on node(s). "COMMAND" '
                              'is passed to the node(s) as is. '
                              'No validation is performed.'))
    args = parser.parse_args()
    
    if args.verbose:
        print "Working..."

    try:
        # turn on warning LED
        warn_led = gpiozero.LED(LED_PIN)
        warn_led.blink(on_time=0.5, off_time=0.5,
                       background=True)

        
        nodes = {'1':[N1_PIN, N1_NAME, None],
                 '2':[N2_PIN, N2_NAME, None],
                 '3':[N3_PIN, N3_NAME, None],
                 '4':[N4_PIN, N4_NAME, None]}

        # pingers
        if (args.action in ['stop', 'restart', 'status']
            and args.hard == False):
            for k in args.nodes:
                try:
                    if power_state(nodes[k][NODE_PIN]) != 0:
                        nodes[k][NODE_PINGER] = gpiozero.PingServer(nodes[k][NODE_NAME])
                except GPIOZeroError:
                    logging.exception('ping error')
                    pass

        if args.action == 'status':
            do_status()
        elif args.action == 'stop':
            do_stop()
        elif args.action == 'start':
            do_start()
        elif args.action == 'restart':
            do_restart()
        elif args.command != None:
            do_command(node_list=args.nodes, cmd=args.command)

    finally:
        # cleanup
        try:
            warn_led.close()
        except:
            pass
        try:
            for k in nodes:
                try:
                    node[k][NODE_PINGER].close()
                except:
                    pass
        except:
            pass

    sys.exit(exit_code)
