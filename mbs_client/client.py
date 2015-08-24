__author__ = 'abdul'

import os

from netutils import fetch_url_json
from errors import MBSClientError
from utils import resolve_path, read_config_json
from makerpy.maker import Maker
import traceback
###############################################################################
# CONSTANTS
###############################################################################
DEFAULT_BS_URL = "http://localhost:9003"

DEFAULT_ENGINE_URL = "http://localhost:8888"

###############################################################################
class Status(object):
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"


###############################################################################
# Generic MBS Client
###############################################################################


class MBSClient(object):

    ###########################################################################
    def __init__(self, api_url):
        self._api_url = api_url


    @property
    def api_url(self):
        return self._api_url

    ###########################################################################
    @api_url.setter
    def api_url(self, url):
        self._api_url = url

    ###########################################################################
    # CLIENT METHODS
    ###########################################################################
    def get_status(self):
        try:
            return self._execute_command("status")
        except IOError:
            return {
                "status": Status.STOPPED
            }
        except ValueError, ve:
            return {
                "status": "UNKNOWN",
                "error": str(ve)
            }
        except Exception, e:
            msg = ("Error while trying to get status. "
                   "Cause: %s. %s" % (e, traceback.format_exc()))
            raise MBSClientError(msg)

    ###########################################################################
    def stop_command(self):
        try:
            self._execute_command("stop")
        except ValueError, ve:
            pass
        except Exception, e:
            msg = ("Error while trying to get backup system status. "
                   "Cause: %s. %s" % (e, traceback.format_exc()))
            raise MBSClientError(msg)


    ###########################################################################
    def delete_backup(self, backup_id):
        params = {
            "backupId": backup_id
        }
        return self._execute_command("delete-backup", params=params)

    ###########################################################################
    def restore_backup(self, backup_id, destination_uri,
                       source_database_name=None, tags=None):
        data = {
            "backupId": backup_id,
            "destinationUri": destination_uri
        }

        if source_database_name:
            data["sourceDatabaseName"] = source_database_name
        if tags:
            data["tags"] = tags

        return self._execute_command("restore-backup", method="POST",
                                     data=data)

    ###########################################################################
    def get_destination_restore_status(self, destination_uri):
        params = {
            "destinationUri": destination_uri
        }

        return self._execute_command("get-destination-restore-status",
                                     method="GET", params=params)

    ###########################################################################
    # HELPERS
    ###########################################################################
    def _execute_command(self, command, params=None, data=None, method=None):
        url = self._command_url(command, params=params)
        return fetch_url_json(url=url, method=method, data=data)

    ###########################################################################
    def _command_url(self, command, params=None):
        url = self.api_url
        if not url.endswith("/"):
            url += "/"
        url += command

        if params:
            url += "?"
            count = 0
            for name, val in params.items():
                if count > 0:
                    url += "&"
                url += "%s=%s" % (name, val)
                count += 1
        return url

###############################################################################
# BackupSystemClient
###############################################################################


class BackupSystemClient(MBSClient):

    ###########################################################################
    def __init__(self, api_url=None):
        url = api_url or DEFAULT_BS_URL
        MBSClient.__init__(self, api_url=url)

    ###########################################################################
    # Backup system client methods
    ###########################################################################

    def get_backup_database_names(self, backup_id):
        params = {
            "backupId": backup_id
        }
        return self._execute_command("get-backup-database-names",
                                     params=params)

    ###########################################################################
    def delete_backup(self, backup_id):
        params = {
            "backupId": backup_id
        }
        return self._execute_command("delete-backup", params=params)

    ###########################################################################
    def restore_backup(self, backup_id, destination_uri,
                       source_database_name=None, tags=None):
        data = {
            "backupId": backup_id,
            "destinationUri": destination_uri
        }

        if source_database_name:
            data["sourceDatabaseName"] = source_database_name
        if tags:
            data["tags"] = tags

        return self._execute_command("restore-backup", method="POST",
                                     data=data)

    ###########################################################################
    def get_destination_restore_status(self, destination_uri):
        params = {
            "destinationUri": destination_uri
        }

        return self._execute_command("get-destination-restore-status",
                                     method="GET", params=params)


###############################################################################
# BackupEngineClient
###############################################################################


class BackupEngineClient(MBSClient):

    ###########################################################################
    def __init__(self, api_url=None):
        url = api_url or DEFAULT_ENGINE_URL
        MBSClient.__init__(self, api_url=url)

    ###########################################################################
    # Backup system client methods
    ###########################################################################
    def cancel_backup(self, backup_id):
        params = {
            "backupId": backup_id
        }
        return self._execute_command("cancel-backup",
                                     params=params, method="POST")

    ###########################################################################
    def cancel_restore(self, restore_id):
        params = {
            "restoreId": restore_id
        }
        return self._execute_command("restore-backup",
                                     params=params, method="POST")

###############################################################################
# configuration and global access
###############################################################################

__backup_system_client__ = None

def backup_system_client():
    global __backup_system_client__

    if __backup_system_client__ is None:
        maker = Maker()
        conf = _get_client_config()
        __backup_system_client__ = maker.make(conf)

    return __backup_system_client__

###############################################################################
def _get_client_config():
    conf_path = resolve_path(os.path.join("~/.mbs", "mbs-api-client.config"))
    if os.path.exists(conf_path):
        return read_config_json("mbs-api-client", conf_path)
    else:
        raise Exception("mbs api client conf %s does not exist")
