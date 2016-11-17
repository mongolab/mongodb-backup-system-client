__author__ = 'abdul'

import os

from errors import MBSClientError
from utils import resolve_path, read_config_json
from makerpy.maker import Maker
import traceback
from carbonio_client.client import CarbonIOClient, HTTPError
import time
import logging

###############################################################################
# LOGGER
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

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
            return self.request_endpoint("get", "status")
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
            return self.request_endpoint("get", "stop" )
        except ValueError, ve:
            pass
        except Exception, e:
            msg = ("Error while trying to get backup system status. "
                   "Cause: %s. %s" % (e, traceback.format_exc()))
            raise MBSClientError(msg)

    ####################################################################################################################
    def request_endpoint(self, method_name, endpoint, *args, **kwargs):
        endpoint_obj = self.carbon_client.get_endpoint(endpoint)
        method_func = getattr(endpoint_obj, method_name)

        logger.info("mbs api %s %s: BEGIN REQUEST" % (method_name.upper(), endpoint_obj.full_url))
        start_time = time.time()

        try:
            response = method_func(*args, **kwargs)
            logger.info("mbs api %s %s: RESPONSE requestId '%s', mbs-api-sever '%s'" %
                        (method_name.upper(),
                         endpoint_obj.full_url,
                         response.headers.get("request-id") or "NONE",
                         response.headers.get("mbs-api-server")))
            return response.json()
        except Exception, ex:
            if isinstance(ex, HTTPError):
                logger.info("mbs api %s %s: RESPONSE requestId '%s', mbs-api-sever '%s'" %
                            (method_name.upper(),
                             endpoint_obj.full_url,
                             ex.response.headers.get("request-id") or "NONE",
                             ex.response.headers.get("mbs-api-server")))
            raise
        finally:
            elapsed = time.time() - start_time
            logger.info("mbs api %s %s: END REQUEST. finished in %.3f seconds" % (method_name.upper(),
                                                                                  endpoint_obj.full_url, elapsed))



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
        return self.request_endpoint("get", "get-backup-database-names", params=params)

    ####################################################################################################################
    def delete_backup(self, backup_id):
        params = {
            "backupId": backup_id
        }
        return self.request_endpoint("get", "delete-backup", params=params)

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

        return self.request_endpoint("post", "restore-backup", body=data)

    ####################################################################################################################
    def get_destination_restore_status(self, destination_uri):
        params = {
            "destinationUri": destination_uri
        }

        return self.request_endpoint("get", "get-destination-restore-status", params=params)


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
        return self.request_endpoint("post", "cancel-backup", options={"params": params})


    ###########################################################################
    def cancel_restore(self, restore_id):
        params = {
            "restoreId": restore_id
        }
        return self.request_endpoint("post", "cancel-restore", options={"params": params})

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
