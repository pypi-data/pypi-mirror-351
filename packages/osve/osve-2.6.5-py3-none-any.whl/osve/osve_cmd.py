#*****************************************************************************#
# This file is subject to the terms and conditions defined in the             #
# file 'LICENSE.txt', which is part of this source code package.              #
#                                                                             #
# No part of the package, including this file, may be copied, modified,       #
# propagated, or distributed except according to the terms contained in       #
# the file 'LICENSE.txt'.                                                     #
#                                                                             #
# (C) Copyright European Space Agency, 2025                                   #
#*****************************************************************************# 


"""
Created on September, 2023

@author: Ricardo Valles Blanco (ESAC)

This module allows to call OSVE using a command line.

"""

import argparse
import logging
import os
import signal
import sys

from .osve import osve


def func_signal_handler(signal, frame):
    """
    Signal handler for the program.

    This function handles the SIGINT signal, providing a clean exit
    message and information about cleanup (not yet implemented).

    :param signal: The signal number.
    :type signal: int
    :param frame: The current stack frame.
    :type frame: frame
    """
    logging.error("Aborting ...")
    logging.info("Cleanup not yet implemented")
    sys.exit(0)


def parse_options():
    """
    Parse command line options.

    This function allows specifying the input parameters:
    - root_scenario_path: Provide the top level path of the scenario
        file_path to be used to resolve the relative paths.
    - session_file_path: Provide the location and name of the
        session file containing all the scenarios files.
    
    :returns: Argument or parameter list passed by command line.
    :rtype: argparse.Namespace
    """

    parser = argparse.ArgumentParser(description='JUICE Operations Simulator & Validation Engine (OSVE)')

    parser.add_argument("-r", "--RootPath",
                        help="Top level path of the scenario file_path to be used to resolve the relative paths",
                        )

    parser.add_argument("-s", "--SessionFile",
                        help="Location and name of the session file containing all the scenarios files",
                        )
    
    parser.add_argument("-v", "--Version",
                        help="OSVE, AGM, and EPS libraries version",
                        action="store_true" )

    args = parser.parse_args()
    return args


def main():
    """
     Entry point for processing.

     This function sets up the signal handler, parses command line options,
     and performs the necessary operations based on the provided arguments.
     """
    signal.signal(signal.SIGINT, func_signal_handler)

    args = parse_options()

    if args.Version:
        the_osve = osve()
        print("")
        print("OSVE LIB VERSION:       ", the_osve.get_app_version())
        print("OSVE AGM VERSION:       ", the_osve.get_agm_version())
        print("OSVE EPS VERSION:       ", the_osve.get_eps_version())
        print("")
        sys.exit(1)

    if args.RootPath:
        if not os.path.exists(args.RootPath):
            logging.error('RootPath "{}" does not exist'.format(args.RootPath))
            sys.exit(0)

    else:
        logging.error('Please provide a RootPath')
        sys.exit(0)

    if args.SessionFile:
        if not os.path.exists(args.SessionFile):
            logging.error('SessionFile "{}" does not exist'.format(args.SessionFile))
            sys.exit(0)

    else:
        logging.error('Please provide a SessionFile')
        sys.exit(0)

    here = os.path.abspath(os.path.dirname(__file__))

    # Get library
    the_osve = osve()
    the_osve.execute(args.RootPath, args.SessionFile)

    os.chdir(here)


def debug():
    """
    Debug: Print exception and stack trace.
    """

    e = sys.exc_info()
    print("type: %s" % e[0])
    print("Msg: %s" % e[1])
    import traceback
    traceback.print_exc(e[2])
    traceback.print_tb(e[2])


if __name__ == "__main__":

    try:
        main()
    except SystemExit as e:
        print("Exit")
    except:
        print("<h5>Internal Error. Please contact JUICE SOC </h5>")
        debug()

    sys.exit(0)
