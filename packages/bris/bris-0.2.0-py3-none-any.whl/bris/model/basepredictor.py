import logging
import math
import os
from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, Union

import numpy as np
import pytorch_lightning as pl
import torch
from anemoi.models.data_indices.index import DataIndex, ModelIndex
from torch.distributed.distributed_c10d import ProcessGroup

from ..checkpoint import Checkpoint
from ..data.datamodule import DataModule
from ..forcings import anemoi_dynamic_forcings, get_dynamic_forcings
from ..utils import check_anemoi_training, timedelta64_from_timestep

LOGGER = logging.getLogger(__name__)


class BasePredictor(pl.LightningModule):
    """
    An abstract class for implementing custom predictors.

    Methods
    -------

    __init__

    set_model_comm_group

    set_reader_groups

    set_static_forcings (abstract)

    forward (abstract)

    advance_input_predict (abstract)

    predict_step (abstract)
    """

    def __init__(
        self,
        *args: Any,
        checkpoints: dict[str, Checkpoint],
        hardware_config: dict,
        **kwargs: Any,
    ):
        """
        Init model_comm* variables for distributed training.

        args:
            checkpoints {"forecaster": checkpoint_object}
            hardware_config {"num_gpus_per_model": int, "num_gpus_per_node": int, "num_nodes": int}
        """

        super().__init__(*args, **kwargs)

        if check_anemoi_training(checkpoints["forecaster"].metadata):
            self.legacy = False

            self.model_comm_group = None
            self.model_comm_group_id = 0
            self.model_comm_group_rank = 0
            self.model_comm_num_groups = 1

        else:
            self.legacy = True

            self.model_comm_group = None
            self.model_comm_group_id = (
                int(os.environ.get("SLURM_PROCID", "0"))
                // hardware_config["num_gpus_per_model"]
            )
            self.model_comm_group_rank = (
                int(os.environ.get("SLURM_PROCID", "0"))
                % hardware_config["num_gpus_per_model"]
            )
            self.model_comm_num_groups = math.ceil(
                hardware_config["num_gpus_per_node"]
                * hardware_config["num_nodes"]
                / hardware_config["num_gpus_per_model"],
            )

    def set_model_comm_group(
        self,
        model_comm_group: ProcessGroup,
        model_comm_group_id: int = None,
        model_comm_group_rank: int = None,
        model_comm_num_groups: int = None,
        model_comm_group_size: int = None,
    ) -> None:
        self.model_comm_group = model_comm_group
        if not self.legacy:
            self.model_comm_group_id = model_comm_group_id
            self.model_comm_group_rank = model_comm_group_rank
            self.model_comm_num_groups = model_comm_num_groups
            self.model_comm_group_size = model_comm_group_size

    def set_reader_groups(
        self,
        reader_groups: list[ProcessGroup],
        reader_group_id: int,
        reader_group_rank: int,
        reader_group_size: int,
    ) -> None:
        self.reader_groups = reader_groups
        self.reader_group_id = reader_group_id
        self.reader_group_rank = reader_group_rank
        self.reader_group_size = reader_group_size

    @abstractmethod
    def set_static_forcings(
        self,
        datareader: Iterable,
    ) -> None:
        pass

    @abstractmethod
    def forward(self, x: torch.Tensor) -> Union[torch.Tensor, list[torch.Tensor]]:
        pass

    @abstractmethod
    def advance_input_predict(
        self,
        x: Union[torch.Tensor, list[torch.Tensor]],
        y_pred: Union[torch.Tensor, list[torch.Tensor]],
        time: np.datetime64,
    ) -> torch.Tensor:
        pass

    @abstractmethod
    def predict_step(self, batch: tuple, batch_idx: int) -> dict:
        pass
