#!/usr/bin/python

# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Copyright (c) 2013, Mathijs Dumon
# All rights reserved.
# Complete license can be found in the LICENSE file.

import multiprocessing
import warnings
import argparse, os
import logging

try:
    import gtk
    gtk.gdk.threads_init() # @UndefinedVariable
except ImportError:
    pass

def _worker_initializer(*args):
    from pyxrd.data import settings
    if settings.CACHE == "FILE":
        settings.CACHE = "FILE_FETCH_ONLY"
    settings.apply_runtime_settings(no_gui=True)

def _initialize_pool():
    # Set this up before we do anything else,
    # creates 'clean' subprocesses
    return multiprocessing.Pool(maxtasksperchild=100, initializer=_worker_initializer)

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename", nargs="?", default="",
        help="A PyXRD project filename"
    )
    parser.add_argument(
        "-s", "--script", default="",
        help="Can be used to pass a script containing a run() function"
    )
    parser.add_argument(
        "-d", "--debug", dest='debug', action='store_const',
        const=True, default=False,
        help='Run in debug mode'
    )
    parser.add_argument(
        "-c", "--clear-cache", dest='clear_cache', action='store_const',
        const=True, default=False,
        help='Clear the cache (only relevant if using filesystem cache)'
    )

    args = parser.parse_args()
    del parser # free some memory
    return args

def _check_for_updates():
    from pyxrd.generic.update import update
    update()

def _setup_logging(debug, log_file):
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=log_file,
                        filemode='w')

    # Get logger:
    logger = logging.getLogger()
    full = logging.Formatter("%(name)s - %(levelname)s: %(message)s")

    # Setup error stream:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if debug else logging.ERROR)
    console.setFormatter(full)
    logger.addHandler(console)

def _apply_settings(args, pool):

    from pyxrd.data import settings
    # apply settings
    settings.apply_runtime_settings(no_gui=args.script, debug=args.debug, pool=pool)

    _setup_logging(settings.DEBUG, settings.LOG_FILENAME)

    # clean out the file cache if asked and from time to time:
    if settings.CACHE == "FILE":
        from pyxrd.generic.caching import memory
        if args.clear_cache:
            memory.clear()
        else:
            from pyxrd.generic.io import get_size, sizeof_fmt
            size = get_size(memory.cachedir, settings.CACHE_SIZE)
            logging.info("Cache size is (at least): %s" % sizeof_fmt(size))
            if size > settings.CACHE_SIZE:
                memory.clear()

def _run_user_script(args):
    """
        Runs the user script specified in the command-line arguments.
    """
    try:
        import imp
        user_script = imp.load_source('user_script', args.script)
    except any as err:
        err.args = "Error when trying to import %s: %s" % (args.script, err.args)
        raise
    user_script.run(args)

def _close_pool(pool):
    # Close the pool:
    logging.info("Closing multiprocessing pool ...")
    pool.close()
    pool.join()

def _run_gui(args, splash=None):
    # Now we can load these:
    from pyxrd.data import settings
    from pyxrd.project.models import Project
    from pyxrd.application.models import AppModel
    from pyxrd.application.views import AppView
    from pyxrd.application.controllers import AppController
    from pyxrd.generic.gtk_tools.gtkexcepthook import plugin_gtk_excepthook

    # Initialize threads

    # Check if a filename was passed, if so try to load it
    project = None
    if args.filename != "":
        try:
            logging.info("Opening project: %s" % args.filename)
            project = Project.load_object(args.filename)
        except IOError:
            logging.info("Could not load project file %s: IOError" % args.filename)
            # FIXME the user should be informed of this in a dialog...

    # Disable unity overlay scrollbars as they cause bugs with modal windows
    os.environ['LIBOVERLAY_SCROLLBAR'] = '0'
    os.environ['UBUNTU_MENUPROXY'] = ""

    if not settings.DEBUG:
        warnings.filterwarnings(action='ignore', category=Warning)

    # Close splash screen
    if splash: splash.close()

    # Nice GUI error handler:
    plugin_gtk_excepthook()

    # setup MVC:
    m = AppModel(project=project)
    v = AppView()
    AppController(m, v)

    # Free this before continuing
    del args
    del project
    del splash

    # lets get this show on the road:
    gtk.main()

def run_gui(args=None):

    # Display a splash screen showing the loading status...
    from pkg_resources import resource_filename # @UnresolvedImport
    from pyxrd.generic.views.splash import SplashScreen
    from pyxrd import __version__
    filename = resource_filename(__name__, "application/icons/pyxrd.png")
    splash = SplashScreen(filename, __version__)

    # Check if this is already provided:
    splash.set_message("Parsing arguments ...")
    if not isinstance(args, argparse.ArgumentParser):
        args = _parse_args()

    # Check for updates
    splash.set_message("Checking for updates ...")
    _check_for_updates()

    # Run GUI:
    splash.set_message("Loading GUI ...")
    _run_gui(args, splash)

def run_main():
    """
        Parsers command line arguments and launches PyXRD accordingly.
    """

    # Setup & parse keyword arguments:
    args = _parse_args()

    # Initialize multiprocessing pool:
    pool = _initialize_pool()

    # Apply settings
    _apply_settings(args, pool)

    try:
        if args.script:
            # Run the specified user script:
            _run_user_script(args)
        else:
            # Run the GUI:
            run_gui(args)
    except:
        raise # re-raise the error
    finally:
        _close_pool(pool)