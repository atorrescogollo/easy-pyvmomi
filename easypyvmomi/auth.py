import ssl
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from pyVim.connect import SmartStubAdapter, VimSessionOrientedStub

class VSphere:

    def __init__(self, host, username, password, port=443, verify=True, **kwargs):
        # connector_func = connect.SmartConnect if verify else connect.SmartConnectNoSSL
        # self.service_instance = connector_func(
        #     host=host,
        #     user=username,
        #     pwd=password,
        #     port=int(port)
        # )

        if not verify and not hasattr(kwargs, 'sslContext'):
            kwargs['sslContext'] = ssl._create_unverified_context()
        # https://github.com/vmware/pyvmomi/issues/347#issuecomment-297591340
        smart_stub = SmartStubAdapter(host=host, port=port, connectionPoolTimeout=0, **kwargs)
        session_stub = VimSessionOrientedStub(smart_stub, VimSessionOrientedStub.makeUserLoginMethod(username, password))
        self.service_instance = vim.ServiceInstance('ServiceInstance', session_stub)

    def __del__(self):
        connect.Disconnect(self.service_instance)
