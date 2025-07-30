import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor

from .config import REFERENCE_VIDEO_SEQUENCE
from .evaluation import calculate_psnr, calculate_ssim
from .stads import AdaptiveSampler
from .random_sampler import RandomSampler
from .stratified_sampler import StratifiedSampler
from .microscope import sample_image_from_video_sequence
from .interpolator import ImageInterpolator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class LaboratoryInstrument:
    image_shape: tuple
    number_of_frames: int
    interpolation_method: str = 'linear'
    initial_sampling: str = 'stratified'
    output_dir: str = 'data/plots'

    def validate_inputs(self):
        # Validate types
        if not (isinstance(self.image_shape, tuple) and
                all(isinstance(x, int) and x > 0 for x in self.image_shape)):
            raise TypeError("image_shape must be a tuple of positive integers.")

        if not (isinstance(self.number_of_frames, int) and self.number_of_frames > 0):
            raise TypeError("number_of_frames must be a positive integer.")

        if not isinstance(self.interpolation_method, str):
            raise TypeError("interpolation_method must be a string.")

        if not isinstance(self.initial_sampling, str):
            raise TypeError("initial_sampling must be a string.")

        if not isinstance(self.output_dir, str):
            raise TypeError("output_dir must be a string.")

        # Validate number_of_frames vs reference video length
        if self.number_of_frames > len(REFERENCE_VIDEO_SEQUENCE):
            raise ValueError("Requested number of frames exceeds available reference video.")

        # Validate frames themselves
        for idx, frame in enumerate(REFERENCE_VIDEO_SEQUENCE[:self.number_of_frames]):
            if not (isinstance(frame, np.ndarray) and frame.dtype == np.uint8):
                raise TypeError(f"Frame at index {idx} is not a uint8 numpy array.")

    def _run_all_samplers_for_sparsity(self, sparsity):
        logging.info(f"Running all samplers for {sparsity}% sparsity")
        results = {
            "AdaptiveSampler": self._run_adaptive_sampler(sparsity),
            "RandomSampler": self._run_random_sampler(sparsity),
            "StratifiedSampler": self._run_stratified_sampler(sparsity)
        }
        return sparsity, results

    def run_experiment1(self):
        logging.info("Running Experiment 1: Sampler comparison across sparsity levels")
        self.validate_inputs()

        sparsities = [10, 15, 20, 30, 50, 75]

        psnr_means = {"AdaptiveSampler": [], "RandomSampler": [], "StratifiedSampler": []}
        psnr_stds = {"AdaptiveSampler": [], "RandomSampler": [], "StratifiedSampler": []}
        ssim_means = {"AdaptiveSampler": [], "RandomSampler": [], "StratifiedSampler": []}
        ssim_stds = {"AdaptiveSampler": [], "RandomSampler": [], "StratifiedSampler": []}

        # Run sequentially (parallel removed for Experiment 1)
        all_results = [self._run_all_samplers_for_sparsity(s) for s in sparsities]

        for sparsity, results in all_results:
            for sampler_name, (psnrs, ssims) in results.items():
                psnr_means[sampler_name].append(np.mean(psnrs))
                psnr_stds[sampler_name].append(np.std(psnrs))
                ssim_means[sampler_name].append(np.mean(ssims))
                ssim_stds[sampler_name].append(np.std(ssims))

        self.save_comparison_plots(sparsities, psnr_means, psnr_stds, ssim_means, ssim_stds)

    def _run_adaptive_sampler(self, sparsity):
        logging.info(f"Running AdaptiveSampler at {sparsity}%")
        sampler = AdaptiveSampler(
            imageShape=self.image_shape,
            initialSampling=self.initial_sampling,
            interpolMethod=self.interpolation_method,
            sparsityPercent=sparsity,
            numberOfFrames=self.number_of_frames
        )
        _, psnrs, ssims = sampler.run()
        return psnrs, ssims

    @staticmethod
    def _process_frame_random_sampler(args):
        instrument, sparsity, frame_idx = args
        sampler = RandomSampler(instrument.image_shape, sparsity)
        y, x = sampler.get_coordinates()
        sampled = sample_image_from_video_sequence(y, x, instrument.image_shape, frame_idx)
        known_points = np.column_stack((y, x))
        values = sampled[y, x]
        interpolator = ImageInterpolator(instrument.image_shape, known_points, values, instrument.interpolation_method)
        reconstructed = np.clip(interpolator.interpolate_image(), 0, 255).astype(np.uint8)
        gt = REFERENCE_VIDEO_SEQUENCE[frame_idx]
        psnr = calculate_psnr(gt, reconstructed)
        ssim = calculate_ssim(reconstructed, gt)
        return psnr, ssim

    def _run_random_sampler(self, sparsity):
        logging.info(f"Running RandomSampler at {sparsity}%")
        logging.info(f"Starting parallel frame processing for RandomSampler at {sparsity}% sparsity")

        with ProcessPoolExecutor() as executor:
            args = [(self, sparsity, i) for i in range(self.number_of_frames)]
            results = list(executor.map(LaboratoryInstrument._process_frame_random_sampler, args))

        return zip(*results)

    @staticmethod
    def _process_frame_stratified_sampler(args):
        instrument, sparsity, frame_idx = args
        sampler = StratifiedSampler(instrument.image_shape, sparsity)
        y, x = sampler.get_coordinates()
        sampled = sample_image_from_video_sequence(y, x, instrument.image_shape, frame_idx)
        known_points = np.column_stack((y, x))
        values = sampled[y, x]
        interpolator = ImageInterpolator(instrument.image_shape, known_points, values, instrument.interpolation_method)
        reconstructed = np.clip(interpolator.interpolate_image(), 0, 255).astype(np.uint8)
        gt = REFERENCE_VIDEO_SEQUENCE[frame_idx]
        psnr = calculate_psnr(gt, reconstructed)
        ssim = calculate_ssim(reconstructed, gt)
        return psnr, ssim

    def _run_stratified_sampler(self, sparsity):
        logging.info(f"Running StratifiedSampler at {sparsity}%")
        logging.info(f"Starting parallel frame processing for StratifiedSampler at {sparsity}% sparsity")

        with ProcessPoolExecutor() as executor:
            args = [(self, sparsity, i) for i in range(self.number_of_frames)]
            results = list(executor.map(LaboratoryInstrument._process_frame_stratified_sampler, args))

        return zip(*results)

    def run_experiment2(self):
        logging.info("Running Experiment 2: Temporal flow impact in AdaptiveSampler")
        self.validate_inputs()
        os.makedirs(self.output_dir, exist_ok=True)

        with ProcessPoolExecutor() as executor:
            future_with = executor.submit(self._run_adaptive_temporal, True)
            future_without = executor.submit(self._run_adaptive_temporal, False)
            psnrs_with, ssims_with = future_with.result()
            psnrs_without, ssims_without = future_without.result()

        frames = list(range(1, len(psnrs_with) + 1))
        self.plot_metric_comparison(frames, psnrs_with, psnrs_without, "PSNR")
        self.plot_metric_comparison(frames, ssims_with, ssims_without, "SSIM")

    def _run_adaptive_temporal(self, with_temporal: bool):
        config = "with" if with_temporal else "without"
        logging.info(f"Running AdaptiveSampler {config} temporal information")

        sampler = AdaptiveSampler(
            imageShape=self.image_shape,
            initialSampling=self.initial_sampling,
            interpolMethod=self.interpolation_method,
            sparsityPercent=50,
            numberOfFrames=self.number_of_frames,
            withTemporal=with_temporal
        )
        _, psnrs, ssims = sampler.run()
        return psnrs, ssims

    def plot_metric_comparison(self, frames, with_values, without_values, metric):
        plt.figure()
        plt.plot(frames, with_values, '-o', label='With Temporal Flow')
        plt.plot(frames, without_values, '-x', label='Without Temporal Flow')
        plt.xlabel("Frame")
        plt.ylabel(metric)
        plt.title(f"{metric} vs Frame")
        plt.legend()
        plt.grid(True)
        filename = f"{metric.lower()}_temporal_comparison.png"
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        logging.info(f"{metric} plot saved to {filename}")

    def save_comparison_plots(self, sparsities, psnr_means, psnr_stds, ssim_means, ssim_stds):
        os.makedirs(self.output_dir, exist_ok=True)
        self._plot_metric(sparsities, psnr_means, psnr_stds, "PSNR")
        self._plot_metric(sparsities, ssim_means, ssim_stds, "SSIM")

    def _plot_metric(self, sparsities, metric_means, metric_stds, metric_name):
        plt.figure()
        for label in metric_means:
            plt.errorbar(sparsities, metric_means[label], yerr=metric_stds[label], fmt='-o', label=label)
        plt.title(f"Mean {metric_name} vs Sparsity")
        plt.xlabel("Sparsity (%)")
        plt.ylabel(metric_name)
        plt.grid(True)
        plt.legend()
        filename = f"{metric_name.lower()}_sampler_comparison.png"
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        logging.info(f"{metric_name} plot saved to {filename}")
