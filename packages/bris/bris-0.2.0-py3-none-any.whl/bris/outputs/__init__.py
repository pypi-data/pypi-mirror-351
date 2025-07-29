import copy
from typing import Optional

import numpy as np

from bris import sources
from bris.predict_metadata import PredictMetadata


def instantiate(name: str, predict_metadata: PredictMetadata, workdir: str, init_args):
    """Creates an object of type name with config

    Args:
        predict_metadata: Contains metadata about the bathc the output will recive
        init_args: Arguments to pass to Output constructor
    """
    if name == "verif":
        # Parse obs sources
        obs_sources = []

        # Convert to dict, since iverriding obs_sources doesn't seem to work with OmegaConf
        args = {**init_args}
        for source in init_args["obs_sources"]:
            for source_name, opts in source.items():
                obs_sources += [sources.instantiate(source_name, opts)]
        args["obs_sources"] = obs_sources
        return Verif(predict_metadata, workdir, **args)

    if name == "netcdf":
        return Netcdf(predict_metadata, workdir, **init_args)

    raise ValueError(f"Invalid output: {name}")


def get_required_variables(name, init_args):
    """What variables does this output require? Return None if it will process all variables
    provided
    """

    if name == "netcdf":
        if "variables" in init_args:
            variables = init_args["variables"]
            if "extra_variables" in init_args:
                for var_name in init_args["extra_variables"]:
                    if var_name == "ws":
                        variables += ["10u", "10v"]
            variables = list(set(variables))
            return variables
        return [None]

    if name == "verif":
        if init_args["variable"] == "ws":
            return ["10u", "10v"]
        return [init_args["variable"]]

    raise ValueError(f"Invalid output: {name}")


class Output:
    """This class writes output for a specific part of the domain"""

    def __init__(
        self, predict_metadata: PredictMetadata, extra_variables: Optional[list] = None
    ):
        """Creates an object of type name with config

        Args:
            predict_metadata: Contains metadata about the batch the output will recieve
        """
        if extra_variables is None:
            extra_variables = []

        predict_metadata = copy.deepcopy(predict_metadata)
        predict_metadata.variables += extra_variables

        self.pm = predict_metadata
        self.extra_variables = extra_variables

    def add_forecast(self, times: list, ensemble_member: int, pred: np.ndarray):
        """Registers a forecast from a single ensemble member in the output

        Args:
            times: List of np.datetime64 objects
            ensemble_member: Which ensemble member is this?
            pred: 3D numpy array with dimensions (leadtime, location, variable)
        """

        # Append extra variables to prediction
        extra_pred = []
        for name in self.extra_variables:
            if name == "ws":
                Ix = self.pm.variables.index("10u")
                Iy = self.pm.variables.index("10v")
                curr = np.sqrt(pred[..., [Ix]] ** 2 + pred[..., [Iy]] ** 2)
                extra_pred += [curr]
            else:
                raise ValueError(f"No recipe to compute {name}")

        pred = np.concatenate([pred] + extra_pred, axis=2)

        assert pred.shape[0] == self.pm.num_leadtimes
        assert pred.shape[1] == len(self.pm.lats)
        assert pred.shape[2] == len(self.pm.variables), (
            pred.shape,
            len(self.pm.variables),
        )
        assert ensemble_member >= 0
        assert ensemble_member < self.pm.num_members

        self._add_forecast(times, ensemble_member, pred)

    def _add_forecast(self, times: list, ensemble_member: int, pred: np.ndarray):
        """Subclasses should implement this"""
        raise NotImplementedError()

    def finalize(self):
        """Finalizes the output. This gets called after all add_forecast calls are done. Subclasses
        can override this, if necessary."""

    def reshape_pred(self, pred):
        """Reshape predictor matrix from points to x,y based on field_shape

        Args:
            pred: 3D numpy array with dimensions (leadtime, location, variable)

        Returns:
            4D numy array with dimensions (leadtime, y, x, variable)
        """
        assert self.pm.field_shape is not None

        T, _L, V = pred.shape
        shape = [T, self.pm.field_shape[0], self.pm.field_shape[1], V]
        pred = np.reshape(pred, shape)
        return pred

    def flatten_pred(self, pred):
        """Reshape predictor matrix on 2D points back to the original 1D set of points

        Args:
            pred: 4D numy array with dimensions (leadtime, y, x, variable)

        Returns:
            3D numpy array with dimensions (leadtime, location, variable)
        """
        assert len(pred.shape) == 4
        T, _Y, _X, V = pred.shape

        shape = [T, self.pm.field_shape[0] * self.pm.field_shape[1], V]
        pred = np.reshape(pred, shape)
        return pred


from .intermediate import Intermediate
from .netcdf import Netcdf
from .verif import Verif
