# -*- coding: utf-8 -*-
# kate: space-indent on; indent-width 4; replace-tabs on;

import json
from StringIO import StringIO
from systemd         import invoke, logged, LockingPlugin, method
from ifconfig.models import NetDevice

def cidr2mask(len):
    """Convert a bit length to a dotted netmask (aka. CIDR to netmask)"""
    mask = ''
    if not isinstance(len, int) or len < 0 or len > 32:
        print "Illegal subnet length: %s (which is a %s)" % (str(len), type(len).__name__)
        return None

    for t in range(4):
        if len > 7:
            mask += '255.'
        else:
            dec = 255 - (2**(8 - len) - 1)
            mask += str(dec) + '.'
        len -= 8
        if len < 0:
            len = 0

    return mask[:-1]


@logged
class SystemD(LockingPlugin):
    dbus_path = "/ifconfig"

    @method(in_signature="", out_signature="")
    def write_interfaces(self):
        self.lock.acquire()
        out = StringIO()
        out.writelines([
            "# THIS FILE HAS BEEN GENERATED BY openATTIC\n",
            "# Do not edit directly, configure via the openATTIC GUI instead.\n",
            "\n"
            ])
        fd = open( "/etc/network/interfaces", "wb" )

        try:
            depends = {}
            autoifs = []

            haveaddr = False

            for interface in NetDevice.objects.all():
                depends[interface.devname] = []

                if interface.dhcp:
                    out.write("iface %s inet dhcp\n" % interface.devname)
                    haveaddr = True
                elif interface.address:
                    if interface.address.is_loopback:
                        out.write("iface %s inet loopback\n" % interface.devname)
                    else:
                        addr = interface.address.address.split("/")
                        out.write("iface %s inet static\n" % interface.devname)
                        out.write("\taddress %s\n" % addr[0])
                        haveaddr = True
                        if len(addr) > 1:
                            try:
                                out.write("\tnetmask %s\n" % cidr2mask(int(addr[1])))
                            except ValueError:
                                out.write("\tnetmask %s\n" % addr[1])
                        else:
                            raise ValueError("Interface %s has an address without a netmask" % interface.devname)
                        if interface.address.gateway:
                            out.write("\tgateway %s\n" % interface.address.gateway)
                        if interface.address.domain:
                            out.write("\tdns-search %s\n" % interface.address.domain)
                        if interface.address.nameservers:
                            out.write("\tdns-nameservers %s\n" % interface.address.nameservers)
                else:
                    out.write("iface %s inet manual\n" % interface.devname)

                if interface.vlanrawdev:
                    base = interface.vlanrawdev
                    depends[interface.devname].append(base)
                    if base == interface:
                        raise ValueError("Vlan %s has ITSELF as its base interface" % interface.devname)
                    out.write("\tvlan-raw-device %s\n" % base.devname)

                if interface.brports.all().count():
                    depends[interface.devname].extend(list(interface.brports.all()))
                    if interface.brports.filter(id=interface.id).count():
                        raise ValueError("Bridge %s has ITSELF as one of its ports" % interface.devname)
                    out.write("\tbridge-ports %s\n" % " ".join([p.devname for p in interface.brports.all()]))

                if interface.slaves.count():
                    depends[interface.devname].extend(list(interface.slaves.all()))
                    if interface.slaves.filter(id=interface.id).count():
                        raise ValueError("Bonding %s has ITSELF as one of its slaves" % interface.devname)

                    out.write("\tslaves %s\n"  % ' '.join( [p.devname for p in interface.slaves.all()] ))
                    out.write("\tbond_mode %s\n"      % interface.bond_mode)
                    out.write("\tbond_miimon %s\n"    % interface.bond_miimon)
                    out.write("\tbond_downdelay %s\n" % interface.bond_downdelay)
                    out.write("\tbond_updelay %s\n"   % interface.bond_updelay)

                if interface.auto:
                    autoifs.append(interface)

                out.write("\n")

            if not haveaddr:
                raise ValueError("There is no interface that has an IP (none with dhcp and none with static address).")

            out.write( "# Interface Dependency Tree:\n" )
            out.write( "# " + str(depends) + "\n" )
            out.write( "\n" )

            while autoifs:
                for interface in autoifs:
                    if not depends[interface.devname]:
                        out.write("auto %s\n" % interface.devname)
                        autoifs.remove(interface)
                        for depiface in depends:
                            if interface in depends[depiface]:
                                depends[depiface].remove(interface)

            out.seek(0)
            fd.write( out.read() )

        finally:
            fd.close()
            self.lock.release()

