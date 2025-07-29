from proxies.mytorch.nn.layers_proxy import DropoutProxy
from torch.Tensor import Tensor

class Dropout:
    def __init__(self, p=0.5, inplace=False):
        self.p = p  
        self.inplace = inplace  
        self.proxy = DropoutProxy(p=p, inplace=inplace)

    def __call__(self, tensor: Tensor):
        return self.proxy.forward(tensor)
