from pyVmomi import vim

class VirtualMachineRaw:
    def __init__(self, vsphere):
        self.vsphere = vsphere
        self.content = self.vsphere.service_instance.RetrieveContent()

    def getAll(self):
        """
        https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/getallvms.py
        """
        container = self.content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True

        containerView = self.content.viewManager.CreateContainerView(
            container, viewType, recursive)
        container.Destroy()

        children = containerView.view
        return children

    def get(self, vmname, output_format='raw'):
        """
        https://github.com/vmware/pyvmomi-community-samples/issues/266#issuecomment-246719664
        """
        vms = self.getAll()
        output_vm = None
        for vm in vms:
            if vm.name == vmname:
                output_vm = vm
                break

        if output_vm and output_format=='json':
            output_vm = self.VM2json(output_vm)

        return output_vm

    def VM2json(self, vm):
        vm_devices = []
        vm_storage = []
        vm_network = []
        for device in vm.config.hardware.device:
            # https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/virtual_machine_device_info.py
            if hasattr(device.backing, 'fileName'): # is storage
                vm_storage.append({
                    'type': type(device).__name__,
                    'label': device.deviceInfo.label,
                    'capacityInKB': int(device.capacityInKB),
                    'datastore': device.backing.datastore.name,
                    'fileName': device.backing.fileName,
                    'diskMode': device.backing.diskMode,
                    'thinProvisioned': device.backing.thinProvisioned
                })
            # https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/getvnicinfo.py
            elif isinstance(device, vim.vm.device.VirtualEthernetCard):
                portGroup = None
                vlanId = None
                vSwitch = None
                if hasattr(device.backing, 'port'):
                    portGroupKey = device.backing.port.portgroupKey
                    dvsUuid = device.backing.port.switchUuid
                    try:
                        dvs = self.content.dvSwitchManager.QueryDvsByUuid(dvsUuid)
                    except:
                        portGroup = "** Error: DVS not found **"
                        vlanId = "NA"
                        vSwitch = "NA"
                    else:
                        pgObj = dvs.LookupDvPortGroup(portGroupKey)
                        portGroup = pgObj.config.name
                        vlanId = str(pgObj.config.defaultPortConfig.vlan.vlanId)
                        vSwitch = str(dvs.name)
                # TODO
                # else:
                #     portGroup = device.backing.network.name
                #     vmHost = vm.runtime.host
                #     # global variable hosts is a list, not a dict
                #     host_pos = hosts.index(vmHost)
                #     viewHost = hosts[host_pos]
                #     # global variable hostPgDict stores portgroups per host
                #     pgs = hostPgDict[viewHost]
                #     for p in pgs:
                #         if portGroup in p.key:
                #             vlanId = str(p.spec.vlanId)
                #             vSwitch = str(p.spec.vswitchName)
                if portGroup is None: portGroup = 'NA'
                if vlanId is None: vlanId = 'NA'
                if vSwitch is None: vSwitch = 'NA'

                vm_network.append({
                    'type': type(device).__name__,
                    'label': device.deviceInfo.label,
                    'macAddress': device.macAddress,
                    'portGroup': portGroup,
                    'vlanId': vlanId,
                    'vSwitch': vSwitch,
                })
            else:
                vm_devices.append({
                    'label': device.deviceInfo.label,
                    'summary': device.deviceInfo.summary,
                })

        # Enrich network info with ipaddresses (virtual nic are ignored)
        for nic in vm.guest.net:
            macAddress = nic.macAddress
            for hw_nic in vm_network:
                if hw_nic['macAddress'] == macAddress:
                    hw_nic['ipAddress'] = list(nic.ipAddress)
                    break

        output = {
            'instanceUuid': vm.config.instanceUuid,
            'biosUuid': vm.config.uuid,
            'version': vm.config.version,
            'vmname': vm.name,
            'numCPU': vm.config.hardware.numCPU,
            'memoryMB': vm.config.hardware.memoryMB,
            'overallStatus': vm.summary.overallStatus,
            'powerState': vm.runtime.powerState,
            'hypervisor': vm.runtime.host.name,
            'guestState': vm.guest.guestState,
            'bootTime': str(vm.runtime.bootTime),
            'guestId': vm.config.guestId,
            'guestFullName': vm.config.guestFullName,
            'vmPathName': vm.summary.config.vmPathName,
            'network': vm_network,
            'storage': vm_storage,
            'other_devices': vm_devices,
        }

        return output
