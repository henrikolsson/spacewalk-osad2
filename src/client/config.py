#!/usr/bin/env python
#
# Copyright (c) 2014-2015 SUSE LLC
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#

import sys

sys.path.append('/usr/share/rhn')

import ConfigParser
import logging
import time
import os

from rhn import rpclib
from up2date_client.config import initUp2dateConfig
from up2date_client import config


class ClientConfig(object):
    def __init__(self, config_path):
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(config_path))
        self.logger = self.get_logger(__name__)
        self.osad_config = self.__get_osad_config()

    def __get_osad_config(self):
        serverrpc = rpclib.Server(uri=self.get_server_url())
        ret = None
        while ret is None:
            self.logger.info("registering as push client with %s..." % self.get_server_url())
            try:
                ret = serverrpc.registration.register_osad(self.get_systemid(), {'client-timestamp': int(time.time())})
            except Exception as e:
                self.ogger.error(e)
                self.logger.info("waiting %d seconds..." % self.get_osad_registry_interval())
                time.sleep(self.get_osad_registry_interval())
        return ret

    def get_server_host(self):
        return self.osad_config['jabber-server']

    def get_system_name(self):
        return self.osad_config['client-name']

    def get_server_producer(self):
        return 'tcp://%s:5555' % self.get_server_host()

    def get_server_consumer(self):
        return 'tcp://%s:5556' % self.get_server_host()

    def get_logger(self, name):
        log_level = logging.DEBUG if self.is_debug() else logging.INFO
        logging.basicConfig(level=log_level, filename=self.config.get('osad', 'logfile'))
        return logging.getLogger(name)

    def is_debug(self):
        return self.config.getint('osad', 'debug_level') > 0

    def get_server_url(self):
        cfg = initUp2dateConfig()
        return cfg['serverURL']

    def get_rhn_check_command(self):
        return self.config.get('osad', 'rhn_check_command')

    def get_osad_registry_interval(self):
        return 20

    def get_default_keys_dir(self):
        return self.config.get('osad', 'certificates')

    def get_server_public_key_file(self):
        return os.path.join(self.get_default_keys_dir(), self.config.get('osad', 'server_public_key'))

    def get_client_secret_key_file(self):
        return os.path.join(self.get_default_keys_dir(), self.config.get('osad', 'client_secret_key'))

    def get_pid_file(self):
        return self.config.get('osad', 'pidfile')

    def get_systemid(self):
        systemid_path = self.config.get('osad', 'systemid')
        with open(systemid_path) as f:
            return f.read()

    def get_ping_topic(self):
        return 'ping'

    def get_system_topic(self):
        return "system:%s"
