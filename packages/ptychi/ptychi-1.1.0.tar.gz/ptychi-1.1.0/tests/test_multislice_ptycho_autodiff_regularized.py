import argparse

import torch
import numpy as np

import ptychi.api as api
from ptychi.api.task import PtychographyTask
from ptychi.utils import get_suggested_object_size, get_default_complex_dtype

import test_utils as tutils


class TestMultislicePtychoAutodiffRegularized(tutils.BaseTester):

    @tutils.BaseTester.wrap_recon_tester(name='test_multislice_ptycho_autodiff_regularized')
    def test_multislice_ptycho_autodiff_regularized(self):
        self.setup_ptychi(cpu_only=False)
        
        data, probe, pixel_size_m, positions_px = self.load_data_ptychodus(
            *self.get_default_input_data_file_paths('multislice_ptycho_AuNi'),
            subtract_position_mean=True
        )
        wavelength_m = 1.03e-10
        
        options = api.AutodiffPtychographyOptions()
        
        options.data_options.data = data
        options.data_options.wavelength_m = wavelength_m
        
        options.object_options.initial_guess = torch.ones([2, *get_suggested_object_size(positions_px, probe.shape[-2:], extra=50)], dtype=get_default_complex_dtype())
        options.object_options.pixel_size_m = pixel_size_m
        options.object_options.slice_spacings_m = np.array([1e-5])
        options.object_options.optimizable = True
        options.object_options.optimizer = api.Optimizers.ADAM
        options.object_options.step_size = 1e-3
        options.object_options.multislice_regularization.enabled = True
        options.object_options.multislice_regularization.weight = 1.0
        options.object_options.multislice_regularization.unwrap_image_grad_method = api.enums.ImageGradientMethods.FOURIER_DIFFERENTIATION
        
        options.probe_options.initial_guess = probe
        options.probe_options.optimizable = True
        options.probe_options.optimizer = api.Optimizers.ADAM
        options.probe_options.step_size = 1e-3
        
        options.probe_position_options.position_x_px = positions_px[:, 1]
        options.probe_position_options.position_y_px = positions_px[:, 0]
        options.probe_position_options.optimizable = True
        options.probe_position_options.optimizer = api.Optimizers.SGD
        options.probe_position_options.step_size = 1e-1
        
        options.reconstructor_options.forward_model_class = api.ForwardModels.PLANAR_PTYCHOGRAPHY
        options.reconstructor_options.loss_function = api.LossFunctions.MSE_SQRT
        options.reconstructor_options.use_double_precision_for_fft = True
        options.reconstructor_options.batch_size = 101
        options.reconstructor_options.num_epochs = 8
        options.reconstructor_options.default_device = api.Devices.GPU
        options.reconstructor_options.random_seed = 123
        options.reconstructor_options.allow_nondeterministic_algorithms = False
        
        task = PtychographyTask(options)
        task.run()

        recon = task.get_data_to_cpu('object', as_numpy=True)
        return recon


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate-gold', action='store_true')
    args = parser.parse_args()

    tester = TestMultislicePtychoAutodiffRegularized()
    tester.setup_method(name="", generate_data=False, generate_gold=args.generate_gold, debug=True)
    tester.test_multislice_ptycho_autodiff_regularized()
