###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.layers_proxy import ReLUProxy

class ReLU:
    def __init__(self, inplace=False):
        self.proxy = ReLUProxy(inplace)

    def __call__(self, tensor):
        # Delegate the call to ReLUProxy for execution
        return self.proxy.forward(tensor)