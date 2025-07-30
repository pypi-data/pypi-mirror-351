import argparse

import torch

import ptychi.api as api
from ptychi.api.task import PtychographyTask
from ptychi.utils import (
    get_suggested_object_size,
    get_default_complex_dtype,
    rescale_probe,
    generate_initial_opr_mode_weights,
)
from ptychi.maths import orthogonalize_gs

import test_utils as tutils


class Test2dPtychoEpieOPR(tutils.TungstenDataTester):
    @tutils.TungstenDataTester.wrap_recon_tester(name="test_2d_ptycho_epie_opr")
    def test_2d_ptycho_epie_opr(self):
        self.setup_ptychi(cpu_only=False)

        data, probe, pixel_size_m, positions_px = self.load_tungsten_data(additional_opr_modes=3)

        options = api.EPIEOptions()
        options.data_options.data = data

        options.object_options.initial_guess = torch.ones(
            [1, *get_suggested_object_size(positions_px, probe.shape[-2:], extra=100)],
            dtype=get_default_complex_dtype(),
        )
        options.object_options.pixel_size_m = pixel_size_m
        options.object_options.optimizable = True
        options.object_options.optimizer = api.Optimizers.SGD
        options.object_options.step_size = 0.1
        options.object_options.alpha = 1

        options.probe_options.initial_guess = probe
        options.probe_options.optimizable = True
        options.probe_options.optimizer = api.Optimizers.SGD
        options.probe_options.step_size = 0.1
        options.probe_options.alpha = 1
        options.probe_options.eigenmode_update_relaxation = 0.1

        options.probe_position_options.position_x_px = positions_px[:, 1]
        options.probe_position_options.position_y_px = positions_px[:, 0]
        options.probe_position_options.optimizable = False

        options.opr_mode_weight_options.initial_weights = generate_initial_opr_mode_weights(
            len(positions_px), probe.shape[0]
        )
        options.opr_mode_weight_options.optimizable = True
        options.opr_mode_weight_options.update_relaxation = 0.1

        options.reconstructor_options.batch_size = 96
        options.reconstructor_options.num_epochs = 32
        options.reconstructor_options.allow_nondeterministic_algorithms = False

        task = PtychographyTask(options)
        task.run()

        recon = task.get_data_to_cpu("object", as_numpy=True)[0]

        return recon

    @tutils.TungstenDataTester.wrap_recon_tester(
        name="test_2d_ptycho_epie_orthogonalize_opr_and_incoherent_modes"
    )
    def test_2d_ptycho_epie_orthogonalize_opr_and_incoherent_modes(self):
        self.setup_ptychi(cpu_only=False)

        data, probe, pixel_size_m, positions_px = self.load_tungsten_data(additional_opr_modes=3)

        options = api.EPIEOptions()
        options.data_options.data = data

        options.object_options.initial_guess = torch.ones(
            [1, *get_suggested_object_size(positions_px, probe.shape[-2:], extra=100)],
            dtype=get_default_complex_dtype(),
        )
        options.object_options.pixel_size_m = pixel_size_m
        options.object_options.optimizable = True
        options.object_options.optimizer = api.Optimizers.SGD
        options.object_options.step_size = 0.1
        options.object_options.alpha = 1

        options.probe_options.initial_guess = probe
        options.probe_options.optimizable = True
        options.probe_options.optimizer = api.Optimizers.SGD
        options.probe_options.step_size = 0.1
        options.probe_options.alpha = 1
        options.probe_options.eigenmode_update_relaxation = 0.1
        options.probe_options.orthogonalize_opr_modes.enabled = True
        options.probe_options.orthogonalize_incoherent_modes.enabled = True

        options.probe_position_options.position_x_px = positions_px[:, 1]
        options.probe_position_options.position_y_px = positions_px[:, 0]
        options.probe_position_options.optimizable = False

        options.opr_mode_weight_options.initial_weights = generate_initial_opr_mode_weights(
            len(positions_px), probe.shape[0]
        )
        options.opr_mode_weight_options.optimizable = True
        options.opr_mode_weight_options.update_relaxation = 0.1

        options.reconstructor_options.batch_size = 96
        options.reconstructor_options.num_epochs = 8
        options.reconstructor_options.allow_nondeterministic_algorithms = False

        task = PtychographyTask(options)
        task.run()

        recon = task.get_data_to_cpu("object", as_numpy=True)[0]

        return recon


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-gold", action="store_true")
    parser.add_argument("--high-tol", action="store_true")
    args = parser.parse_args()

    tester = Test2dPtychoEpieOPR()
    tester.setup_method(name="", generate_data=False, generate_gold=args.generate_gold, debug=True)
    tester.test_2d_ptycho_epie_opr()
    tester.test_2d_ptycho_epie_orthogonalize_opr_and_incoherent_modes()
