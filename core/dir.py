import os

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))
MODELDIR = os.path.join(BASEDIR, "models")
FILESDIR = os.path.join(BASEDIR, "files")

LOGSDIR = os.path.join(BASEDIR, "logs")
LOGFILE = os.path.join(LOGSDIR, "hub.log")

os.makedirs(LOGSDIR, exist_ok=True)
os.makedirs(MODELDIR, exist_ok=True)
os.makedirs(FILESDIR, exist_ok=True)