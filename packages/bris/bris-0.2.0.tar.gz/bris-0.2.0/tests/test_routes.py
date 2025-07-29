import os

import bris.routes


class FakeDataModule:
    def __init__(self):
        self.field_shape = [[None, [1, 2]], [None]]

    @property
    def grids(self):
        ret = dict()
        ret[0] = [1, 2]
        ret[1] = [1]
        return ret

    @property
    def latitudes(self):
        return [[1, 1, 2], [1]]

    @property
    def longitudes(self):
        return self.latitudes

    @property
    def altitudes(self):
        return [[0, 100, 200], [300]]

    @property
    def name_to_index(self):
        return [{"2t": 0, "10u": 1, "10v": 2}, {"100v": 0, "100u": 1}]


class FakeCheckpointObject:
    @property
    def model_output_name_to_index(self):
        return [{"2t": 0, "10u": 1, "10v": 2}, {"100v": 0, "100u": 1}]


def test_get():
    config = list()
    filename = os.path.dirname(os.path.abspath(__file__)) + "/files/verif_input.nc"
    config += [
        {
            "decoder_index": 0,
            "domain_index": 0,
            "outputs": [
                {
                    "verif": {
                        "filename": "nordic/2t/%R.nc",
                        "variable": "2t",
                        "units": "C",
                        "thresholds": [0, 10, 20],
                        "quantile_levels": [0.1, 0.9],
                        "obs_sources": [{"verif": {"filename": filename}}],
                    }
                }
            ],
        },
        {
            "decoder_index": 0,
            "domain_index": 1,
            "outputs": [
                {
                    "netcdf": {
                        "filename_pattern": "%Y%m%d.nc",
                    }
                }
            ],
        },
        {
            "decoder_index": 1,
            "domain_index": 0,
            "outputs": [
                {
                    "netcdf": {
                        "filename_pattern": "%Y%m%d.nc",
                        "variables": ["100u"],
                    }
                }
            ],
        },
    ]
    data_module = FakeDataModule()
    checkpoint_object = FakeCheckpointObject()
    checkpoints = {"forecaster": checkpoint_object}
    workdir = "testdir"
    leadtimes = range(66)
    num_members = 2

    required_variables = bris.routes.get_required_variables(config, checkpoint_object)
    correct_variables = {0: ["2t", "10u", "10v"], 1: ["100u"]}
    for key in required_variables:
        assert set(required_variables[key]) == set(correct_variables[key])

    _ = bris.routes.get(
        config, len(leadtimes), num_members, data_module, checkpoints, workdir
    )


if __name__ == "__main__":
    test_get()
