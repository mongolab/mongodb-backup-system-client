__author__ = 'abdul'

import os

from errors import MBSClientError
from utils import resolve_path, read_config_json
from makerpy.maker import Maker
import traceback
from carbonio_client.client import CarbonIOClient
###############################################################################
# CONSTANTS
###############################################################################
DEFAULT_BS_URL = "http://localhost:9003"

DEFAULT_ENGINE_URL = "http://localhost:8888"

DEFAULT_TIMEOUT = 10 * 60 # 10 minutes

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
        self._client_options = {
            "timeout": DEFAULT_TIMEOUT
        }

        self._carbon_client = None

    ###########################################################################
    @property
    def carbon_client(self):
        if self._carbon_client is None:
            self._carbon_client = CarbonIOClient(self.api_url, options=self._client_options)
        return self._carbon_client


    ###########################################################################
    @property
    def api_url(self):
        return self._api_url

    @api_url.setter
    def api_url(self, url):
        self._api_url = url

    ###########################################################################
    # CLIENT METHODS
    ###########################################################################
    def get_status(self):
        try:
            return self.carbon_client.get_endpoint("status").get()
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
            self.carbon_client.get_endpoint("stop").get()
        except ValueError, ve:
            pass
        except Exception, e:
            msg = ("Error while trying to get backup system status. "
                   "Cause: %s. %s" % (e, traceback.format_exc()))
            raise MBSClientError(msg)


########################################################################################################################
# BackupSystemClient
########################################################################################################################


class BackupSystemClient(MBSClient):

    ####################################################################################################################
    def __init__(self, api_url=None):
        url = api_url or DEFAULT_BS_URL
        MBSClient.__init__(self, api_url=url)

    ####################################################################################################################
    # Backup system client methods
    ####################################################################################################################

    def get_backup_database_names(self, backup_id):
        params = {
            "backupId": backup_id
        }
        return self.carbon_client.get_endpoint("get-backup-database-names").get(params=params).json()

    ####################################################################################################################
    def delete_backup(self, backup_id):
        params = {
            "backupId": backup_id
        }
        return self.carbon_client.get_endpoint("delete-backup").get(params=params).json()

    ####################################################################################################################
    def restore_backup(self, backup_id, destination_uri,
                       source_database_name=None, tags=None,
                       no_index_restore=None, no_users_restore=None, no_roles_restore=None):
        data = {
            "backupId": backup_id,
            "destinationUri": destination_uri
        }

        if source_database_name:
            data["sourceDatabaseName"] = source_database_name
        if tags:
            data["tags"] = tags

        if no_index_restore:
            data["noIndexRestore"] = no_index_restore

        if no_users_restore:
            data["noUsersRestore"] = no_users_restore

        if no_roles_restore:
            data["noRolesRestore"] = no_roles_restore

        return self.carbon_client.get_endpoint("restore-backup").post(body=data).json()

    ####################################################################################################################
    def get_destination_restore_status(self, destination_uri):
        params = {
            "destinationUri": destination_uri
        }

        return self.carbon_client.get_endpoint("get-destination-restore-status").get(params=params).json()


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
        return self.carbon_client.get_endpoint("cancel-backup").post({"params": params}).json()

    ###########################################################################
    def cancel_restore(self, restore_id):
        params = {
            "restoreId": restore_id
        }
        return self.carbon_client.get_endpoint("restore-backup").post({"params": params}).json()

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
