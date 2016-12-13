# -*- coding: utf-8 -*-

"""
 *  Copyright (C) 2011-2016, it-novum GmbH <community@openattic.org>
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

from django.conf import settings
from .distro import distro_settings

distro_settings()

LV_UTIL_DESCRIPTION = "Utilization for %s"
LV_PERF_DESCRIPTION = "Disk stats for %s"
TRAFFIC_DESCRIPTION = "Traffic on %s"
CPUTIME_DESCRIPTION = "CPU Time"

RRD_BASEDIR = getattr(settings, "NAGIOS_RRD_BASEDIR", "/var/lib/pnp4nagios/perfdata")
RRD_PATH = getattr(settings, "NAGIOS_RRD_PATH",
                   "/var/lib/pnp4nagios/perfdata/%(host)s/%(serv)s.rrd")
XML_PATH = getattr(settings, "NAGIOS_XML_PATH",
                   "/var/lib/pnp4nagios/perfdata/%(host)s/%(serv)s.xml")
CMD_PATH = getattr(settings, "NAGIOS_CMD_PATH", "/var/lib/nagios3/rw/nagios.cmd")
STATUS_DAT_PATH = getattr(settings, "NAGIOS_STATUS_DAT_PATH", "/var/cache/nagios3/status.dat")

NAGIOS_CFG_PATH = getattr(settings, "NAGIOS_CFG_PATH", "/etc/nagios3/nagios.cfg")
CONTACTS_CFG_PATH = getattr(settings, "NAGIOS_CONTACTS_CFG_PATH",
                            "/etc/nagios3/conf.d/openattic_contacts.cfg")
NAGIOS_SERVICES_CFG_PATH = getattr(settings, "NAGIOS_SERVICES_CFG_PATH")

BINARY_NAME = getattr(settings, "NAGIOS_BINARY_NAME", "nagios3")
SERVICE_NAME = getattr(settings, "NAGIOS_SERVICE_NAME", "nagios3")

RRDCACHED_SOCKET = getattr(settings, "NAGIOS_RRDCACHED_SOCKET", None)
