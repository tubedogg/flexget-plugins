from __future__ import unicode_literals, division, absolute_import
from builtins import *  # noqa pylint: disable=unused-import, redefined-builtin
from future.utils import native

import glob
import logging
import os
import re
import sys

from flexget import plugin
from flexget.event import event

log = logging.getLogger('app_deluge_find')

def find_deluge():
    if not (sys.platform.startswith('darwin')):
        return
    deluge_dir = '/Applications/Deluge.app/Contents/Resources/lib/python2.7'
    log.debug('Looking for deluge install in %s', deluge_dir)
    if not os.path.isdir(deluge_dir):
        return
    deluge_egg = glob.glob(os.path.join(deluge_dir, 'deluge-*-py2.?.egg'))
    if not deluge_egg:
        return
    minor_version = int(re.search(r'py2\.(\d).egg', deluge_egg[0]).group(1))
    if minor_version != sys.version_info[1]:
        log.verbose('Cannot use deluge from install directory because its python version doesn\'t match.')
        return
    log.debug('Found deluge install in `%s`, adding to sys.path', deluge_dir)
    sys.path.append(deluge_dir)
    for item in os.listdir(deluge_dir):
        if item.endswith(('.egg', '.zip')):
            sys.path.append(os.path.join(deluge_dir, item))

find_deluge()

class DelugePathPlugin(object):
    """Appends sys.path before deluge plugin tries to test dependencies"""
    schema = {'type': 'boolean'}

    @plugin.priority(130)
    def on_task_start(self, task, config):
        log.debug('path modified')

@event('plugin.register')
def register_plugin():
    plugin.register(DelugePathPlugin, 'app_deluge_find', api_ver=2)
