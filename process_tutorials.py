#!/usr/bin/env python
"""
Process tutorials notebooks for publication in documentation.
"""
import logging
import os
import subprocess
import sys
from shutil import copyfile, copytree, rmtree
from gammapy.extern.pathlib import Path
from gammapy.scripts.jupyter import test_notebook


logging.basicConfig(level=logging.INFO)


def ignorefiles(d, files): return [
    f
    for f in files
    if os.path.isfile(os.path.join(d, f))
    and f[-6:] != '.ipynb'
    and f[-4:] != '.png'
]


def ignoreall(d, files): return [
    f
    for f in files
    if os.path.isfile(os.path.join(d, f))
    and f[-6:] != '.ipynb'
]


def main():

    if len(sys.argv) != 2:
        logging.info("Usage:")
        logging.info("python process_tutorials.py tutorials")
        logging.info("python process_tutorials.py tutorials/mynotebook.ipynb")
        sys.exit()

    env_vars = ["GAMMAPY_EXTRA", "GAMMA_CAT", "GAMMAPY_FERMI_LAT_DATA", "CTADATA"]
    for var in env_vars:
        if var not in os.environ:
            logging.info(var + " environment variable not set.")
            logging.info("Running notebook tests requires this environment variable.")
            logging.info("Exiting now.")
            sys.exit()

    # prepare folder structure
    pathsrc = Path(sys.argv[1])
    path_temp = Path("temp")
    path_empty_nbs = Path("tutorials")
    path_filled_nbs = Path("docs") / "notebooks"
    path_static_nbs = Path("docs") / "_static" / "notebooks"

    rmtree(str(path_temp), ignore_errors=True)
    path_temp.mkdir(parents=True, exist_ok=True)
    path_filled_nbs.mkdir(parents=True, exist_ok=True)
    path_static_nbs.mkdir(parents=True, exist_ok=True)

    if pathsrc == path_empty_nbs:
        rmtree(str(path_temp), ignore_errors=True)
        rmtree(str(path_static_nbs), ignore_errors=True)
        rmtree(str(path_filled_nbs), ignore_errors=True)
        copytree(str(path_empty_nbs), str(path_temp), ignore=ignorefiles)
    elif pathsrc.exists():
        notebookname = pathsrc.name
        pathdest = path_temp / notebookname
        copyfile(str(pathsrc), str(pathdest))
    else:
        logging.info("Notebook file does not exist.")
        sys.exit()

    # strip and blackformat
    subprocess.call("gammapy jupyter --src temp black", shell=True)
    subprocess.call("gammapy jupyter --src temp strip", shell=True)

    # test /run
    passed = True
    for path in path_temp.glob("*.ipynb"):
        if not test_notebook(path):
            passed = False

    # convert into scripts
    # copy generated filled notebooks to doc
    # if passed:

    if pathsrc == path_empty_nbs:
        # copytree is needed to copy subfolder images
        copytree(str(path_empty_nbs), str(path_static_nbs), ignore=ignoreall)
        for path in path_static_nbs.glob("*.ipynb"):
            subprocess.call(
                "jupyter nbconvert --to script '{}'".format(str(path)), shell=True
            )
        copytree(str(path_temp), str(path_filled_nbs), ignore=ignorefiles)
    else:
        pathsrc = path_temp / notebookname
        pathdest = path_static_nbs / notebookname
        copyfile(str(pathsrc), str(pathdest))
        subprocess.call(
            "jupyter nbconvert --to script '{}'".format(str(pathdest)), shell=True
        )
        pathdest = path_filled_nbs / notebookname
        copyfile(str(pathsrc), str(pathdest))

    # else:
    #    logging.info("Tests have not passed.")
    #    logging.info("Tutorials not ready for documentation building process.")
    #    rmtree(str(path_static_nbs), ignore_errors=True)

    # tear down
    rmtree(str(path_temp), ignore_errors=True)


if __name__ == "__main__":
    main()