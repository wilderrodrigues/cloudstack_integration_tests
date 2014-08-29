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

import XenAPI
import sys

session = XenAPI.Session(sys.argv[1])
session.login_with_password(sys.argv[2],sys.argv[3])

for x in session.xenapi.VM.get_all():
    if not session.xenapi.VM.get_is_a_template(x) and not session.xenapi.VM.get_is_control_domain(x):
        name = session.xenapi.VM.get_name_label(x)
        print "Virtual Machine found : " + name
        try:
            print "\tSending shutdown to " + name
            session.xenapi.VM.hard_shutdown(x)
        except Exception:
            print "\tShutdown failed, attempt destroy"
        print "\tSending destroy to " + name
        session.xenapi.VM.destroy(x)

for x in session.xenapi.SR.get_all():
    if ("nfs" == session.xenapi.SR.get_type(x) or "lvm" == session.xenapi.SR.get_type(x)) :
        print "SR : " + session.xenapi.SR.get_name_label(x) + " (" + session.xenapi.SR.get_type(x) + ")"
        for vdi in session.xenapi.SR.get_VDIs(x):
            vdi_name = session.xenapi.VDI.get_uuid(vdi) + " (" + session.xenapi.VDI.get_name_label(vdi) + ")"
            if session.xenapi.VDI.get_managed(vdi) and session.xenapi.VDI.get_type(vdi) == "user":
                print "VDI: " + vdi_name
                print "\tDestroying : " + vdi_name
                try:
                    session.xenapi.VDI.destroy(vdi)
                except Exception:
                    print "\tDestroy failed, attemt to forget it"
                    session.xenapi.VDI.forget(vdi)
        if ("nfs" == session.xenapi.SR.get_type(x)) :
            for pbd in session.xenapi.SR.get_PBDs(x):
                pbd_name = session.xenapi.PBD.get_uuid(pbd)
                hostname = session.xenapi.host.get_name_label(session.xenapi.PBD.get_host(pbd))
                print "This SR is attached to : " + hostname
                print "\tUnplugging"
                session.xenapi.PBD.unplug(pbd)
            print "Destroying SR"
            session.xenapi.SR.forget(x)

for host in session.xenapi.host.get_all():
    hostname = session.xenapi.host.get_name_label(host)
    print "Host : " + hostname
    for tag in session.xenapi.host.get_tags(host) :
        print "\tRemoving tag " + tag
        session.xenapi.host.remove_tags(host, tag)