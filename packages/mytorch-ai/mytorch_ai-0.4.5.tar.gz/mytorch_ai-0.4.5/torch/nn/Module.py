from proxies.mytorch.nn.module_proxy import ModuleProxy
from torch.cqbase import CQBase
    
class  Module(CQBase):
    def __init__(self, uuid=None):
        CQBase.__init__(self)
        self.proxy = ModuleProxy()
        self.training = True  # Default just like PyTorch

        if uuid is None:
            uuid = self.proxy.create_module_on_server()
        self.set_uuid(uuid)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if isinstance(value, Module):
            # Register submodule UUID with parent proxy
            if hasattr(self, 'proxy') and hasattr(value, 'uuid'):
                self.proxy.register_child_module(name, value.uuid)

    def set_uuid(self, uuid):
        self.uuid = uuid
        self.proxy.uuid = uuid

    # It is probably possible to make a generic fix for the _in_super_call logic.
    def forward(self, input_data):
        # Save the original value of _in_super_call
        original_in_super_call = getattr(self.local_data, '_in_super_call', False)
        # Set _in_super_call to True to indicate that the method is being called from a super() call
        self.local_data._in_super_call = True
        try:
            # Call the forward method on the server using the proxy
            return self.proxy.forward(input_data)
        finally:
            # Restore the original value of _in_super_call
            self.local_data._in_super_call = original_in_super_call

    def __call__(self, input_data):
        return self.forward(input_data)

    def state_dict(self) -> dict:
        return self.proxy.state_dict()

    def load_state_dict(self, dict):
        return self.proxy.load_state_dict(dict)
    
    def to(self, device):
        self.proxy.to_device(device)
        return self

    def parameters(self):
        return self.proxy.parameters()

    def half(self):
        return self.proxy.half()

    def cuda(self):
        return self.proxy.to_device("cuda")

    def cpu(self):
        return self.proxy.to_device("cpu")
    
    def eval(self):
        self.training = False
        self.proxy.eval()
        # manually call .eval() on known submodules
        for attr_name in dir(self):
            try:
                attr = getattr(self, attr_name)
                if hasattr(attr, "eval") and callable(attr.eval):
                    attr.eval()
            except Exception:
                continue
        return self

    def train(self, mode=True):
        self.training = mode
        self.proxy.train(mode)
        # manually call .train() on known submodules
        for attr_name in dir(self):
            try:
                attr = getattr(self, attr_name)
                if hasattr(attr, "train") and callable(attr.train):
                    attr.train(mode)
            except Exception:
                continue
        return self