#!/usr/bin/python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# script to empty out a xen server.
#
# based on https://github.com/spark404/cs-functional-test/blob/master/xapi_cleanup_xenservers.py

import XenAPI
import sys
import traceback

session = XenAPI.Session(sys.argv[1])
session.login_with_password(sys.argv[2], sys.argv[3])

for ref in session.xenapi.VM.get_all():
    name = session.xenapi.VM.get_name_label(ref)
    if session.xenapi.VM.get_is_a_template(ref):
        continue
    if session.xenapi.VM.get_is_control_domain(ref):
        continue

    print "Virtual Machine found: %s (uuid: %s)" % (name, ref.replace('OpaqueRef:', ''))

    try:
        print "\tSending shutdown"
        session.xenapi.VM.hard_shutdown(ref)
    except XenAPI.Failure:
        traceback.print_exc()
        print "\tShutdown failed, will attempt destroy anyway"
    print "\tSending destroy"
    session.xenapi.VM.destroy(ref)

for ref in session.xenapi.SR.get_all():
    name = session.xenapi.SR.get_name_label(ref)
    sr_type = session.xenapi.SR.get_type(ref)
    print "SR found: %s (uuid: %s, type: %s)" % (name, ref.replace('OpaqueRef:', ''), sr_type)
    if sr_type != "nfs" and sr_type != "lvm":
        print "\tSR type %s, skipping" % sr_type
        continue

    for vdi in session.xenapi.SR.get_VDIs(ref):
        vdi_name = session.xenapi.VDI.get_uuid(vdi) + " (" + session.xenapi.VDI.get_name_label(vdi) + ")"
        if session.xenapi.VDI.get_managed(vdi) and session.xenapi.VDI.get_type(vdi) == "user":
            print "VDI: " + vdi_name
            print "\tDestroying : " + vdi_name
            try:
                session.xenapi.VDI.destroy(vdi)
            except XenAPI.Failure:
                print "\tDestroy failed, attemt to forget it"
                session.xenapi.VDI.forget(vdi)
    if sr_type == "nfs":
        for pbd in session.xenapi.SR.get_PBDs(ref):
            pbd_name = session.xenapi.PBD.get_uuid(pbd)
            hostname = session.xenapi.host.get_name_label(session.xenapi.PBD.get_host(pbd))
            print "This SR is attached to : " + hostname
            print "\tUnplugging"
            session.xenapi.PBD.unplug(pbd)
        print "Destroying SR"
        session.xenapi.SR.forget(ref)

for ref in session.xenapi.host.get_all():
    name = session.xenapi.host.get_name_label(ref)
    print "Host found: %s (uuid: %s)" % (name, ref.replace('OpaqueRef:', ''))
    for tag in session.xenapi.host.get_tags(ref):
        print "\tRemoving tag " + tag
        session.xenapi.host.remove_tags(ref, tag)

for ref in session.xenapi.VLAN.get_all():
    name = session.xenapi.VLAN.get_name_label(ref)
    print "VLAN found: %s (uuid: %s)" % (name, ref.replace('OpaqueRef:', ''))
    print "\tSending destroy"
    session.xenapi.VLAN.destroy(ref)

for ref in session.xenapi.network.get_all():
    name = session.xenapi.network.get_name_label(ref)
    print "Network found: %s (uuid: %s)" % (name, ref.replace('OpaqueRef:', ''))
    config = session.xenapi.network.get_other_config(ref)
    if 'is_host_internal_management_network' in config and \
            config['is_host_internal_management_network']:
        print "\tHost internal network, skipping"
        continue
    print "\tSending destroy"
    try:
        session.xenapi.network.destroy(ref)
    except XenAPI.Failure, e:
        code = ''
        details = getattr(e, 'details', None)
        if details:
            if isinstance(details, basestring):
                code = details
            else:
                try:
                    # noinspection PyUnresolvedReferences
                    code = details[0]
                except TypeError:
                    code = str(details)
        if code == 'NETWORK_CONTAINS_PIF':
            print "\tNetwork contains PIF, destroy failed, ignoring"
        else:
            raise
