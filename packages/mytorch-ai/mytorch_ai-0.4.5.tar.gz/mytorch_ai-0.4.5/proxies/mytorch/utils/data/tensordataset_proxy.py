###############################################################################
# Copyright (c) 2024-2025 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.base_proxy import BaseProxy
from torch.utils.data.Dataset import Dataset
from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler

class TensorDatasetProxy(BaseProxy):
    def __init__(self):
        super().__init__()
        self.logger = Logger.get_logger()
        self.channel = ServerConnection.get_active_connection()

    def createTensorDatasetOnServer(self, dataset: Dataset):
        uuids = [data.uuid for data in dataset]
        self.uuid, self.len = self.generic_call("torch.utils.data", 
                                                "TensorDataset", 
                                                uuids,
                                                call_type="constructor")
        return self.uuid, self.len
    