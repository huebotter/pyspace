#!/usr/bin/env python
""" Create pySPACE center (basic software configuration and data folder)

This file must be run with python.

.. note:: In future this script shall create not only the basic configuration
          folder, but also move the relevant code to site-packages
          and install the required or even the optional dependencies.

.. todo:: Make this script a real installation script.
"""

from distutils.core import setup
import os
import sys
import shutil
import warnings
from os.path import expanduser
home = expanduser("~")

import platform
CURRENTOS = platform.system()

email = 'ric-pyspace-dev@dfki.de'

classifiers = ["Development Status :: 1 - Production/Stable",
               "Intended Audience :: Developers",
               "Intended Audience :: Education",
               "Intended Audience :: Science/Research",
               "License :: None",
               "Operating System :: Linux",
               "Operating System :: OS X",
               "Programming Language :: Python",
               "Programming Language :: Python :: 2",
               "Topic :: Scientific/Engineering :: Information Analysis",
               "Topic :: Scientific/Engineering :: Benchmark",
               "Topic :: Scientific/Engineering :: Mathematics"]

def get_module_code():
    # keep old python compatibility, so no context managers
    init_file = open(os.path.join(os.getcwd(), 'pySPACE', '__init__.py'))
    module_code = init_file.read()
    init_file.close()
    return module_code

def throw_bug():
    raise ValueError('Can not get pySPACE parameters!\n'
                     'Please report a bug to ' + email)

try:
    import ast

    def get_extract_variable(tree, variable):
        for node in ast.walk(tree):
            if type(node) is ast.Assign:
                try:
                    if node.targets[0].id == variable:
                        print node.targets
                        return node.value.s
                except Exception,e:
                    raise
                    pass
        throw_bug()

    def get_ast_tree():
        return ast.parse(get_module_code())

    def get_version():
        tree = get_ast_tree()
        return get_extract_variable(tree, '__version__')

    def get_short_description():
        return "pySPACE is a **Signal Processing And Classification Environment** "
        tree = get_ast_tree()
        return get_extract_variable(tree, '__short_description__')

    def get_long_description():
        tree = get_ast_tree()
        return ast.get_docstring(tree)
except ImportError:
    import re

    def get_variable(pattern):
        m = re.search(pattern, get_module_code(), re.M + re.S + re.X)
        if not m:
            throw_bug()
        return m.group(1)

    def get_version():
        return get_variable(r'^__version__\s*=\s*[\'"](.+?)[\'"]')

    def get_short_description():
        text = get_variable(r'''^__short_description__\s*=\s*  # variable name and =
                            \\?\s*(?:"""|\'\'\')\\?\s*         # opening quote with backslash
                            (.+?)
                            \s*(?:"""|\'\'\')''')              # closing quote
        return text.replace(' \\\n', ' ')

    def get_long_description():
        return get_variable(r'''^(?:"""|\'\'\')\\?\s*          # opening quote with backslash
                            (.+?)
                            \s*(?:"""|\'\'\')''')              # closing quote

def create_directory(path):
    """ Create the given directory path recursively

    Copy from pySPACE.tools.filesystem
    """
    parts = path.split(os.sep)
    subpath = ""
    for part in parts[1:]:
        subpath += os.sep + part
        if not os.path.exists(subpath):
            try:
                os.mkdir(subpath)
            except OSError as (err_no, strerr):
                import errno
                # os.path.exists isn't secure on gpfs!
                if not err_no == errno.EEXIST:
                    raise

def save_copy(src, dest):
    """ Check if file exists and is new before copying

    Otherwise a new file name is created.
    """
    if not os.path.exists(dest):
        shutil.copy2(src, dest)
    elif dest.endswith(".yaml"):
        import yaml
        d = yaml.load(open(dest))
        s = yaml.load(open(src))
        if not d == s:
            dest = dest[:-5] + "_new.yaml"
            save_copy(src, dest)
    elif dest.endswith(".csv") or dest.endswith(".rst"):
        pass
    else:
        dest += ".new"
        save_copy(src, dest)

setup_message = """
Creating (or modifying) pySPACEcenter
-------------------------------------

The pySPACEcenter directory is created in your home directory.
It will include subdirectories for specs, storage with some basic examples and
a more elaborate example folder.
Furthermore, the basic configuration file *config.yaml* will be created.
You might want to have a look at this file to find out, what you can change
in your basic configuration.
To simplify the standard execution, links will be created to the main
software scripts called *launch.py*, *launch_live.py* and
*performance_results_analysis.py*.

It is not yet possible to use these commands outside the folders as normal
command line arguments. Moreover, this script is currently only creating
the pySPACE usage folder. It is not yet installing the needed dependencies,
mentioned in the documentation and it is leaving the software, where it is
and it is not moving it to site-packages, as it is usual for other setup
scripts. This will hopefully change in future.
"""


def setup_package():
    """ Copy configuration files to pySPACEcenter folder in the home dir

    If files are already existing, they are not replaced, but new versions are
    additionally stored.
    """
    print setup_message
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    create_directory(os.path.join(home, "pySPACEcenter"))

    # generate OS-independent shortcut scripts to the run interface
    generate_shortcuts(os.path.join(home, "pySPACEcenter"))
    # create_directory(os.path.join(home, "pySPACEcenter","examples"))
    create_directory(os.path.join(home, "pySPACEcenter","specs"))
    create_directory(os.path.join(home, "pySPACEcenter","storage"))
    src_conf_file = os.path.join(src_path, "docs", "examples", "conf",
                                 "example.yaml")
    dest_conf_file = os.path.join(home, "pySPACEcenter","config.yaml")
    save_copy(src_conf_file,dest_conf_file)

    examples = os.path.join(src_path,"docs","examples")
    # copying examples folder
    for folder, _, files in os.walk(examples):
        new_folder=os.path.join(home, "pySPACEcenter", "examples",
                                folder[len(examples)+1:])
        for file in files:
            if not file.startswith("."):
                create_directory(new_folder)
                save_copy(os.path.join(src_path, folder, file),
                          os.path.join(new_folder, file))
    # copying important examples to normal structure to have a start
    for folder, _, files in os.walk(examples):
        new_folder=os.path.join(home, "pySPACEcenter",folder[len(examples)+1:])
        for file in files:
            if  "conf" in folder[len(examples)+1:] or \
                ".rst" in file or \
                file.startswith("."):
                    pass
            #"example" in file or "example_summary" in folder:
            elif "example" in file \
                    or "example_summary" in folder[len(examples)+1:] \
                    or file=="functions.yaml"\
                    or "template" in file\
                    or folder.endswith("templates") \
                    or folder.endswith("examples"):
                create_directory(new_folder)
                save_copy(os.path.join(src_path, folder,file),
                          os.path.join(new_folder, file))

    print "The pySPACEcenter should be available now."

def generate_blacklist():
    """
    This function tries to import all the pySPACE modules available.
    If a certain module does not have the necessary dependencies installed,
    it will be blacklisted and not imported in further usages of the software

    Once the user installs the missing dependency, he or she can run the setup
    script with the soft option enabled i.e.::

        python setup.py --soft

    which will only refresh the blacklisted nodes.
    """
    blacklist = []
    missing_dependencies = []
    for dirpath, dirnames, files in os.walk('pySPACE'):
        for file in files:
            if "__init__" in file or file.endswith(".py") == False:
                continue

            the_module = os.path.join(dirpath, file)
            if CURRENTOS == 'Windows':
                the_module = the_module.replace('\\', '.')[:-3]
            else:
                the_module = the_module.replace('/', '.')[:-3]
            try:
                __import__(the_module)
            except Exception, e:
                missing_dependencies.append(e.message)
                blacklist.append(file)
            except:
                pass



    try:
        latest_config = home+'/pySPACEcenter/config.yaml'
        config_file = open(latest_config, 'r+')
    except:
        import glob
        print "The default config file was not found. Modifying the latest" \
              "version available."
        latest_config = max(glob.iglob(home+'/pySPACEcenter/*.yaml'),
                            key=os.path.getctime)
        config_file = open(latest_config, 'r+')

    content = config_file.read()
    blacklist_wrote_to_file = False
    new_content = ""
    for line in content.split('\n'):
        if "blacklisted_nodes" in line:
            new_content += "blacklisted_nodes: " + str(blacklist)
            blacklist_wrote_to_file = True
        else:
            new_content += line + "\n"
    if not blacklist_wrote_to_file:
        new_content += "\nblacklisted_nodes: "+str(blacklist)

    if len(blacklist) > 0:
        print "--> The following nodes are blacklisted and henceforth" \
              " excluded from usage within pySPACE"
        print "\n       > "+"\n       > ".join(blacklist)

        print "\n  > If you want to use the above modules, please fix the " \
              "following errors"
        print "\n       --> "+"\n       --> ".join(missing_dependencies) + "\n"



    config_file.seek(0)
    config_file.write(new_content)
    config_file.truncate()
    config_file.close()

#
#    try:
#        shutil.copytree(os.path.join(src_path,"docs","examples"),os.path.join(home, "pySPACEcenter","examples"))
#    except:
#        pass
#
#    # check that we have a version
#    version = get_version()
#    short_description = get_short_description()
#    long_description = get_long_description()
#    # Run build
#    os.chdir(src_path)
#    sys.path.insert(0, src_path)
#
#    setup(name = 'pySPACE', version=version,
#          author = 'pySPACE Developers',
#          author_email = email,
#          maintainer = 'pySPACE Developers',
#          maintainer_email = email,
#          license = "http://pyspace.github.io/pyspace/license.html",
#          platforms = ["Linux, OSX"],
#          url = 'https://github.com/pyspace/',
#          download_url = 'https://github.com/pyspace/pyspace/archive/master.zip',
#          description = short_description,
#          long_description = long_description,
#          classifiers = classifiers,
#          packages = ['pySPACE', 'pySPACE.missions', 'pySPACE.resources', 'pySPACE.environments',
#                      'pySPACE.tests', 'pySPACE.tools', 'pySPACE.run'],
#          package_data = {}
#          )

def generate_shortcuts(pySPACEcenter_path):
    """
    This function generates and writes the launcher shortcut inside the
    pySPACEcenter directory. This shortcut is OS-independent and should
    be used when running pySPACE

    Initially, the links to the launch scripts in pySPACE were done using
    symbolic linking::

        os.symlink(os.path.join(src_path, "pySPACE", "run", "launch_live.py"),
                   os.path.join(home, "pySPACEcenter", "launch_live.py"))

    The method above only works on Unix-systems and as such, the following
    less elegant but fully functional method is preferred.
    """
    PATTERN = r"""#!/usr/bin/env python
# THIS FILE WAS GENERATED AUTOMATICALLY
# Adjust it only if you know what you're doing
# The purpose of this script is to act as a system independent shortcut

import sys
import os

argv = sys.argv
command = "python %(path)s"
for c in argv[1:]:
    command +=' '+c
os.system(command)
""" # variables: path

    # obtain the absolute path of the launcher
    launch_path = os.path.join(os.path.abspath(os.path.curdir),
                               "pySPACE",
                               "run",
                               "launch.py")
    launch_live_path = os.path.join(os.path.abspath(os.path.curdir),
                                    "pySPACE",
                                    "run",
                                    "launch_live.py")
    perf_res_analysis_path = os.path.join(os.path.abspath(os.path.curdir),
                                          "pySPACE",
                                          "run",
                                          "gui",
                                          "performance_results_analysis.py")

    # replace any special characters that might occur
    launch_path = launch_path.replace(os.sep,
                                      "\\" + os.sep)
    launch_live_path = launch_live_path.replace(os.sep,
                                                "\\" + os.sep)
    perf_res_analysis_path = perf_res_analysis_path.replace(os.sep,
                                                            "\\" + os.sep)

    # write the paths in the predefined pattern
    launch_shortcut = PATTERN % dict(path=launch_path)
    launch_live_shortcut = PATTERN % dict(path=launch_live_path)
    perf_res_analysis_shortcut = PATTERN % dict(path=perf_res_analysis_path)

    # create, write and close the new launch file
    shortcut_file = open(os.path.join(pySPACEcenter_path,
                                      "launch.py"),
                         'w')
    shortcut_file.write(launch_shortcut)
    os.fchmod(shortcut_file.fileno(), 0775)
    shortcut_file.close()

    shortcut_file = open(os.path.join(pySPACEcenter_path,
                                      "launch_live.py"),
                         'w')
    shortcut_file.write(launch_live_shortcut)
    os.fchmod(shortcut_file.fileno(), 0775)
    shortcut_file.close()

    shortcut_file = open(os.path.join(pySPACEcenter_path,
                                      "performance_results_analysis.py"),
                         'w')
    shortcut_file.write(perf_res_analysis_shortcut)
    os.fchmod(shortcut_file.fileno(), 0775)
    shortcut_file.close()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--blacklist', default=False,
                        action='store_true',
                        help='Determines whether a hard install should be ' +
                             'performed; use this option when you\'ve installed ' +
                             'new dependencies and want to let pySPACE know ' +
                             'that the blacklist must be updated.')

    args = parser.parse_args()

    if args.blacklist == True:
        # If the soft version of the install is desired, the only action
        # performed by the script is to refresh the blacklisted nodes
        # which did not initially have the necessary dependencies
        generate_blacklist()
        pass
    else:
        setup_package()
        generate_blacklist()
