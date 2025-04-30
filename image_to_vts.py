from typing import Literal

import h5py
import nibabel
import nrrd
import numpy as np
import pydicom
import pyvista as pv


# NOTE: might want option to export as h5... really good compression! And anonymized!
class MedicalImage:
    def __init__(self, path: str, file_format: Literal["auto", "nrrd", "dicom", "nifti"] = "auto"):
        self.path = path
        self.image, self.metadata = self.load_image(file_format)

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

        if file_format == "nrrd":
            image, metadata = self.load_nrrd(self.path)

        elif file_format == "dicom":
            ds = pydicom.dcmread(self.path)
            image = ds.pixel_array
            metadata = ds

        elif file_format == "nifti":
            img = nibabel.load(self.path)
            image = img.get_fdata()
            metadata = img.header
        else:
            raise ValueError("Unsupported file format")

        return image, metadata

    # NOTE: this is how we do it for NRRD. nifti and dicom may work differently...
    def generate_grid(self):
        grid_size = self.metadata["dimensions"]
        xv = np.arange(0, grid_size[0] + 1, dtype=np.float32)
        yv = np.arange(0, grid_size[1] + 1, dtype=np.float32)
        zv = np.arange(0, grid_size[2] + 1, dtype=np.float32)

        X, Y, Z = np.meshgrid(xv, yv, zv, indexing="ij")

        # ravel to 1D and transform all coordinates at once
        coords = np.vstack((X.ravel(), Y.ravel(), Z.ravel()))
        transformed_coords = np.dot(self.metadata["transform"], coords) + self.metadata["origin"][:, np.newaxis]

        X = transformed_coords[0, :].reshape(X.shape)
        Y = transformed_coords[1, :].reshape(Y.shape)
        Z = transformed_coords[2, :].reshape(Z.shape)

        # convert coordinates to float32 to save space
        X = np.asarray(X, dtype=np.float32)
        Y = np.asarray(Y, dtype=np.float32)
        Z = np.asarray(Z, dtype=np.float32)

        return X, Y, Z

    def export_to_vts(self, output_path: str):
        X, Y, Z = self.generate_grid()
        grid = pv.StructuredGrid(X, Y, Z)
        grid.cell_data["Image Intensity"] = self.image.flatten(order="F")
        grid.field_data["Space Origin"] = self.metadata["origin"]
        plane_normals = np.linalg.inv(self.metadata["transform"])
        # I don't really know why I'm inverting this but it gives the right result if you want to draw planes along the axial, saggital, and coronal planes
        grid.field_data["Image Axis 1"] = plane_normals[0]
        grid.field_data["Image Axis 2"] = plane_normals[1]
        grid.field_data["Image Axis 3"] = plane_normals[2]
        grid.save(output_path, binary=True)

    def export_to_h5(self, output_path: str):
        with h5py.File(output_path, "w") as f:
            f.create_dataset("image", data=self.image)
            f.create_dataset("metadata", data=self.metadata)  # NOTE: pretty sure this doesn't work...
            f.create_dataset("origin", data=self.metadata["origin"])
            f.create_dataset("transform", data=self.metadata["transform"])
            f.create_dataset("dimensions", data=self.metadata["dimensions"])

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
    um16_mra = MedicalImage("test/603 MRA Last Phase.nrrd")
    um16_mra.export_to_vts("603_MRA_Last_Phase_NEW_CODE.vts")


if __name__ == "__main__":
    main()
