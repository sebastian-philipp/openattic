# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; replace-tabs on;

"""
 *  Copyright (C) 2011-2012, it-novum GmbH <community@open-attic.org>
 *
 *  openATTIC is free software; you can redistribute it and/or modify it
 *  under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; version 2.
 *
 *  This package is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
"""

from rpcd.handlers import ModelHandler
from rpcd.handlers import ProxyModelHandler

from ifconfig.models import Host
from zfs.models import Zpool, Zfs

class ZpoolHandler(ModelHandler):
    model = Zpool

class ZpoolProxy(ProxyModelHandler, ZpoolHandler):
    pass


class ZfsHandler(ModelHandler):
    model = Zfs

    def _override_get(self, obj, data):
        data['fs'] = {
            'mounted':     obj.mounted,
            }
        if obj.mounted:
            data['fs']['stat'] = obj.stat
        data["status"] = obj.status
        return data


class ZfsProxy(ProxyModelHandler, ZfsHandler):
    pass

RPCD_HANDLERS = [ZpoolProxy, ZfsProxy]
