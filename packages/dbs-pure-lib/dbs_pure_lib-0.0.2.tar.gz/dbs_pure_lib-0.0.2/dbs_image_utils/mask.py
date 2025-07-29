import dataclasses
import os
import pathlib
from typing import Dict, List, Tuple, Any


import nibabel as nib
import numpy as np


"""An instance of subcortical mask which is an instance  """


class SubcorticalMask:
    x_bds = None
    y_bds = None
    z_bds = None
    n_x = None
    n_y = None
    n_z = None

    _precomp_mask_3d = None

    def recompute_mask(self, min_coord, max_coord, offset_max):
        n_x = abs(int(((max_coord[0] + 2 * offset_max) - min_coord[0]) / 2)) + 1
        n_y = abs(int(((max_coord[1] + 2 * offset_max) - min_coord[1]) / 2) + 1)
        n_z = abs(int(((max_coord[2] + 2 * offset_max) - min_coord[2]) / 2) + 1)

        self.x_bds = [(min_coord[0] - offset_max) + x * 2 for x in range(n_x)]
        self.y_bds = [(min_coord[1] - offset_max) + x * 2 for x in range(n_y)]
        self.z_bds = [(min_coord[2] - offset_max) + x * 2 for x in range(n_z)]

        self.n_x = n_x
        self.n_y = n_y
        self.n_z = n_z
        self._precomp_mask_3d = None
        self.min_p = min_coord
        self.max_p = max_coord
        pass

    def recompute_mask_shape(self, min_coord, max_coord, offset_max, shape=(16, 16, 16)):
        """
        recomputes mask with a shape
        """
        dx = (max_coord[0] - min_coord[0] + 2 * offset_max) / (shape[0] + 1)
        dy = (max_coord[1] - min_coord[1] + 2 * offset_max) / (shape[1] + 1)
        dz = (max_coord[2] - min_coord[2] + 2 * offset_max) / (shape[2] + 1)

        self.x_bds = [(min_coord[0] - offset_max) + x * dx for x in range(shape[0])]
        self.y_bds = [(min_coord[1] - offset_max) + x * dy for x in range(shape[1])]
        self.z_bds = [(min_coord[2] - offset_max) + x * dz for x in range(shape[2])]

        self.n_x = shape[0]
        self.n_y = shape[1]
        self.n_z = shape[2]
        self._precomp_mask_3d = None
        self.min_p = min_coord
        self.max_p = max_coord

    def __init__(self, filename=None):
        if filename == None:
            return
        # Load the mask file and get the data as a numpy array
        mask_f = nib.load(filename)
        mask_im = mask_f.get_fdata()

        # Get the minimum and maximum x, y, and z indices of the mask
        arr_X = np.where(mask_im.max(axis=(1, 2)) == 1)[0]
        min_x, max_x = arr_X[0], arr_X[-1]

        arr_X = np.where(mask_im.max(axis=(0, 2)) == 1)[0]
        min_y, max_y = arr_X[0], arr_X[-1]

        arr_X = np.where(mask_im.max(axis=(0, 1)) == 1)[0]
        min_z, max_z = arr_X[0], arr_X[-1]

        # Get the affine transformation matrix for the mask image
        to_world = mask_f.affine

        # Transform the minimum and maximum indices to world coordinates
        min_p = np.dot(to_world, np.array([min_x, min_y, min_z, 1]))[:3]
        max_p = np.dot(to_world, np.array([max_x, max_y, max_z, 1]))[:3]

        # Make the coordinates mirrorable in MNI space
        max_x = 0
        if max_p[0] < 0:
            max_x = 0 - max(abs(max_p[0]), abs(min_p[0]))
        else:
            max_x = max(abs(max_p[0]), abs(min_p[0]))
        min_x = 0 - max_x

        # Calculate the number of discretized points in each dimension
        n_x = abs(int((max_x - min_x) / 2)) + 1
        n_y = abs(int((max_p[1] - min_p[1]) / 2) + 1)
        n_z = abs(int((max_p[2] - min_p[2]) / 2) + 1)

        # Generate the bounds for the discretized points in each dimension
        if (max_p[0] - min_p[0]) < 0:
            self.x_bds = [min_x - x * 2 for x in range(abs(n_x))]
        else:
            self.x_bds = [min_x + x * 2 for x in range(n_x)]
        self.y_bds = [min_p[1] + x * 2 for x in range(n_y)]
        self.z_bds = [min_p[2] + x * 2 for x in range(n_z)]

        self.n_x = n_x
        self.n_y = n_y
        self.n_z = n_z

        self.min_p = min_p
        self.max_p = max_p
        pass

    def get_dimensions(self):
        """
        return: X Y Z
        """
        return self.n_x, self.n_y, self.n_z

    @property
    def shape(self):
        return self.n_x, self.n_y, self.n_z

    def get_coords_list(self):
        # Generate a meshgrid of the x, y, and z coordinates
        X, Y, Z = np.meshgrid(self.x_bds, self.y_bds, self.z_bds, indexing='ij')

        # Stack the meshgrid arrays along the last axis to create a 3D array of coordinates
        coords = np.stack((X, Y, Z), axis=-1)

        # Flatten the 3D array to a 2D array and return it
        return coords.reshape((-1, 3))

    def get_coords_3d(self):
        if self._precomp_mask_3d is None:
            res = np.zeros((self.n_x, self.n_y, self.n_z, 3))
            x_bds, y_bds, z_bds = np.meshgrid(self.x_bds, self.y_bds, self.z_bds, indexing='ij')
            res[:, :, :, 0] = x_bds
            res[:, :, :, 1] = y_bds
            res[:, :, :, 2] = z_bds
            self._precomp_mask_3d = res.copy()
        return self._precomp_mask_3d.copy()


    def copy(self, obj):
        self.x_bds = obj.x_bds
        self.y_bds =obj.y_bds
        self.z_bds = obj.z_bds
        self.n_x = obj.n_x
        self.n_y = obj.n_y
        self.n_z = obj.n_z
        self._precomp_mask_3d = obj._precomp_mask_3d
        self.min_p = obj.min_p
        self.max_p = obj.max_p
