import pathlib
from typing import Literal

import h5py
import nibabel
import nrrd
import numpy as np
import pydicom


# NOTE: might want option to export as h5... really good compression! And anonymized!
class MedicalImage:
    def __init__(self, path: str, file_format: Literal["auto", "nrrd", "dicom", "nifti"] = "auto"):
        self.path = path
        self.image, self.metadata = self.load_image(self.path, file_format)

    def load_image(self, file_format: Literal["auto", "nrrd", "dicom", "nifti"] = "auto"):
        if file_format == "auto":
            if self.path.endswith(".nrrd"):
                file_format = "nrrd"
            elif self.path.endswith(".dcm"):
                file_format = "dicom"
            elif self.path.endswith(".nii") or self.path.endswith(".nii.gz"):
                file_format = "nifti"
            else:
                raise ValueError("Unsupported file format")

        if self.path.endswith(".nrrd"):
            image, metadata = nrrd.read(self.path)

        elif self.path.endswith(".dcm"):
            ds = pydicom.dcmread(self.path)
            image = ds.pixel_array
            metadata = ds

        elif self.path.endswith(".nii") or self.path.endswith(".nii.gz"):
            img = nibabel.load(self.path)
            image = img.get_fdata()
            metadata = img.header
        else:
            raise ValueError("Unsupported file format")

        return image, metadata

    def transform_image(self):
        return -1

    def export_to_vts(self, output_path: str):
        return -1

    # FIXME: IMPLEMENT THIS
    @staticmethod
    def load_dicom(path: str):
        ds = pydicom.dcmread(path)
        image = ds.pixel_array
        metadata = ds
        return image, metadata

    @staticmethod
    def load_nrrd(path: str) -> tuple[np.ndarray, dict]:
        image, header = nrrd.read(path)

        metadata = {
            "transform": header["space directions"].T,
            "origin": header["space origin"],
            "dimensions": header["sizes"],
        }

        return image, metadata

    # FIXME: IMPLEMENT THIS
    @staticmethod
    def load_nifti(path: str):
        img = nibabel.load(path)
        image = img.get_fdata()
        metadata = img.header
        return image, metadata


def main():
    dont_delete = np.array([0, 0, 0])
    with h5py.File("vts.h5", "w") as f:
        for path in pathlib.Path().rglob("*.dcm"):
            print(path)
            image = MedicalImage(str(path))
            image.load_image()
