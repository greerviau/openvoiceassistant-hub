import subprocess
import threading
import typing
import time
import os
import logging
logger = logging.getLogger("updater")

from core.dir import BASEDIR

UPDATE_BRANCHES = ["main", "develop", "release"]

class Updater:
    def __init__(self):
        self.update_available = False
        self.updating = False
        self.version = open(os.path.join(BASEDIR, "VERSION")).read()
        self.update_version = ""
        # Get current branch
        try:
            self.current_branch = self.run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        except Exception as e:
            logger.error("Failed to fetch branch")
            self.current_branch = "undefined"
        logger.info(f"Current branch: {self.current_branch}")

    def run_cmd(self, command: typing.List[str]) -> str:
        return subprocess.check_output(command, encoding="utf8").strip()

    def check_for_updates(self):
        if not self.updating:
            if self.current_branch not in UPDATE_BRANCHES:
                logger.warning(f"You are not on an update branch, skipping update check")
                return

            try:
                # Fetch latest changes from remote repository
                self.run_cmd(["git", "fetch"])

                # Get latest commit hashes for local and remote branches
                local_commit = self.run_cmd(["git", "rev-parse", "HEAD"])
                remote_commit = self.run_cmd(["git", "rev-parse", f"origin/{self.current_branch}"])

                # Compare commit hashes
                if local_commit != remote_commit:
                    logger.info("Updates available!")
                    latest_version = subprocess.check_output(["git", "show", f"origin/{self.current_branch}:VERSION"]).decode("utf-8").strip()
                    self.update_version = f"v{latest_version}" if latest_version != self.version else f"v{self.version}-patch"
                    self.update_available = True
                else:
                    logger.info("No updates available.")
                    self.update_available = False
            except Exception as e:
                logger.error("Failed to check for updates")
        else:
            logger.warning("Update in progress, cant check for new updates")
    
    def update(self):
        if self.update_available:
            try:
                self.updating = True
                self.update_available = False
                self.run_cmd(["git", "pull", "origin", self.current_branch])
                self.run_cmd(["./scripts/install.sh"])
            except Exception as e:
                logger.exception("Exception while updating")
                self.updating = False
        else:
            logger.warning("Cannot update, no updates available")
            self.updating = False

    def start(self):
        run_thread = threading.Thread(target=self.run, daemon=True)
        run_thread.start()
    
    def run(self):
        while True:
            if not self.update_available:
                self.check_for_updates()
            time.sleep(3600)    # Check every hour