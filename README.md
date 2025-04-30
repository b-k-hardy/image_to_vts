# IMAGE_TO_VTS

The code in this repository is designed to take in medical image formats and export these images to the VTK XML structured grid data type. While this is not the most efficient storage mechanism, this is the only easily-accessible file type for use in ParaView.

## Features

- Ability to align different images in ParaView for nice visualizations
  - No need to "eyeball" with the Transform filter
- More consistent performance in ParaView (sometimes native medical imaging formats glitch out ParaView)

## Pros and Cons of .vts Format

### Pros

- Allows for any kind of arbitrary orientation compared to .vti (image) and .vtr (rectilinear grid), which both require data to exist in the standard basis. This benefit is most relevant when trying to overlay images that exist in different coordinate systems. This is the main pro, but it is a big one since ParaView does not consider orientation when directly reading in NRRD, NIfTI, or DICOM data.
- ParaView filters work best with VTK data. Some NIfTI's, for example, cause ParaView to fail when attempting to read them in. Creating a custom ParaView reader is quite tedious, so having a place to ensure that image data is in a format that plays nice with ParaView first is more practical.

### Cons

- The .vts format requires that the coordinate data be stored explicitly. This is inefficient and kind of annoying -- the NRRD format, for example, just requires spacing and directional data since it is restricted to raster data (**N**early **R**aw **R**aster **D**ata).
- Data that does not exist in the standard basis / coordinate system $(\hat{e}_x, \hat{e}_y, \hat{e}_z)$ can be quite annoying in ParaView. I may look into a way to automate the rotation of data such that it exists in the standard basis. This would allow for storage in the .vti data type (which is substantially more efficient) and easier post-processing in ParaView.

## Medical Image Types Implemented / to be Implemented

- [x] NRRD
- [ ] NIfTI
  - [ ] NIfTI1
  - [ ] NIfTI2
- [ ] DICOM

## Miscellaneous Notes

Time-series data must be implemented with separate .vts files (e.g., image01.vts, image02.vts, ...). If you plan on generating vts files for an entire series, it is recommended to dump the output into a separate folder.

I'm still working on making sure that vector-valued data (basically just 4D-Flow) has the correct orientation.