from pathlib import Path
from typing import Optional, Tuple, Dict

import numpy as np
import torch.utils.data
from torch import Tensor
from torchio.transforms.preprocessing.intensity.histogram_standardization import DEFAULT_CUTOFF, _get_percentiles, \
    _get_average_mapping, HistogramStandardization, TypeLandmarks, _normalize
from tqdm.auto import tqdm


class HistogramStandartisation():

    def __init__(self, landmarks):
        self.landmarks = landmarks

    def apply_normalization(
            self,
            image_array: Tensor,
    ) -> Tensor:

        normalized = _normalize(torch.Tensor(image_array), self.landmarks, mask=None)
        return normalized.numpy()


    @classmethod
    def train(
            cls,
            images: torch.utils.data.Dataset,
            cutoff: Optional[Tuple[float, float]] = None,

    ) -> np.ndarray:
        """Extract average histogram landmarks from images used for training.

        Args:
            images: Dataset used to train 
            cutoff: Optional minimum and maximum quantile values,
                respectively, that are used to select a range of intensity of
                interest. Equivalent to :math:`pc_1` and :math:`pc_2` in
                `Nyúl and Udupa's paper <http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.204.102&rep=rep1&type=pdf>`_.
            mask_path: Path (or list of paths) to a binary image that will be
                used to select the voxels use to compute the stats during
                histogram training. If ``None``, all voxels in the image will
                be used.
            masking_function: Function used to extract voxels used for
                histogram training.
            output_path: Optional file path with extension ``.txt`` or
                ``.npy``, where the landmarks will be saved.

        Example:

            >>> import torch
            >>> import numpy as np
            >>> from pathlib import Path
            >>> from torchio.transforms import HistogramStandardization
            >>>
            >>> t1_paths = ['subject_a_t1.nii', 'subject_b_t1.nii.gz']
            >>> t2_paths = ['subject_a_t2.nii', 'subject_b_t2.nii.gz']
            >>>
            >>> t1_landmarks_path = Path('t1_landmarks.npy')
            >>> t2_landmarks_path = Path('t2_landmarks.npy')
            >>>
            >>> t1_landmarks = (
            ...     t1_landmarks_path
            ...     if t1_landmarks_path.is_file()
            ...     else HistogramStandardization.train(t1_paths)
            ... )
            >>> torch.save(t1_landmarks, t1_landmarks_path)
            >>>
            >>> t2_landmarks = (
            ...     t2_landmarks_path
            ...     if t2_landmarks_path.is_file()
            ...     else HistogramStandardization.train(t2_paths)
            ... )
            >>> torch.save(t2_landmarks, t2_landmarks_path)
            >>>
            >>> landmarks_dict = {
            ...     't1': t1_landmarks,
            ...     't2': t2_landmarks,
            ... }
            >>>
            >>> transform = HistogramStandardization(landmarks_dict)
        """  # noqa: E501

        quantiles_cutoff = DEFAULT_CUTOFF if cutoff is None else cutoff
        percentiles_cutoff = 100 * np.array(quantiles_cutoff)
        percentiles_database = []
        a, b = percentiles_cutoff  # for mypy
        percentiles = _get_percentiles((a, b))
        for i in tqdm(range(len(images))):
            tensor, _ = images[i]

            mask = np.ones_like(tensor, dtype=bool)

            array = tensor.numpy()
            percentile_values = np.percentile(array[mask], percentiles)
            percentiles_database.append(percentile_values)
        percentiles_database_array = np.vstack(percentiles_database)
        mapping = _get_average_mapping(percentiles_database_array)

        return mapping
