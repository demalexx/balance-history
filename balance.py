import sys
import time
import logging
from argparse import ArgumentParser
from traceback import format_exc
from os.path import expanduser, isfile

from config import CONFIG
from sources import source_classes
from graphs import Graphs


def main():
    try:
        # Initialization
        args = handle_args()
        init_logging(args)

        # Getting data from external resources
        balances = []
        for s in args.sources:
            src = source_classes[s]()
            balance = src.get_balance()
            balances.append((s, balance))

            logging.info(u'%s: %s', s, balance)

        # Write received data (and only if all sources returned data successfully)
        now_str = time.strftime(u'%d.%m.%Y %H:%M')
        for source, balance in balances:
            log_fname = u'logs/%s.log' % source

            with open(log_fname, u'a') as f:
                f.write(u'%s, %.2f\n' % (now_str, balance.value))

            logging.info(u'Updated file %s' % log_fname)

        # Generate html file with fancy graphs
        Graphs().generate_html()
    except Exception as e:
        # We want to notify user that error happened
        write_exception(e)
        raise


def init_logging(args):
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format=u'%(message)s', level=level)


def handle_args():
    parser = ArgumentParser(description=u'Get data from sites (like phone balance) using given modules')
    parser.add_argument(u'sources', nargs=u'+', choices=source_classes.keys(), help=u'Sources to get data from')
    parser.add_argument(u'--verbose', action=u'store_true', help=u'Be verbose when getting data')
    return parser.parse_args()


def write_exception(exc):
    """Create file on desktop with traceback to notify user about error"""

    desktop_folder = u'%s/Desktop' % (expanduser(u'~%s' % CONFIG[u'desktop_user']))
    msg = u'Command line arguments: %s\n' % u' '.join(sys.argv)
    msg += format_exc()

    # Create new file for each error
    i = 1
    fname = u'%s/BALANCE-HISTORY-FAILED.txt' % desktop_folder
    while isfile(fname):
        fname = u'%s/BALANCE-HISTORY-FAILED-%d.txt' % (desktop_folder, i)
        i += 1

    with open(fname, u'w') as f:
        f.write(msg)


if __name__ == u'__main__':
    main()
