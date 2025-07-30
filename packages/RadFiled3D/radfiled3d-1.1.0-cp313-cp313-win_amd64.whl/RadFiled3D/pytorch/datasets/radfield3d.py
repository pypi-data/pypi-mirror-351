from .cartesian import CartesianFieldDataset
from RadFiled3D.RadFiled3D import CartesianRadiationField, RadiationFieldMetadataV1, HistogramVoxel
from .base import MetadataLoadMode
from RadFiled3D.pytorch.types import RadiationField, TrainingInputData, DirectionalInput, RadiationFieldChannel, PositionalInput
from RadFiled3D.pytorch.helpers import RadiationFieldHelper
import torch
from torch import Tensor
from typing import Union


class RadField3DDataset(CartesianFieldDataset):
    """
    A dataset for radiation fields generated with the RadField3D generator.
    This dataset is a subclass of CartesianFieldDataset and provides methods to access radiation fields.
    It is designed to work with the RadField3D format, which includes metadata and radiation fields.
    The dataset can be initialized with a list of file paths or a zip file containing the radiation fields.
    It supports loading radiation fields and their metadata, and provides a method to access the radiation field data as PyTorch tensors.
    The dataset returns instances of TrainingInputData, which contains the input as a DirectionalInput as well as the ground truth as a RadiationField.
    The shape of the ground truth tensors is (c, x, y, z) c is the number of channels (typically 32 for spectra and 1 for all other layers), and (x, y, z) are the dimensions of the radiation field.
    The shape of the input tensor is (3,) for the tube direction and (n,) for the tube spectrum, where n is the number of bins in the tube spectrum.
    """
    def __init__(self, file_paths: list[str] = None, zip_file: str = None, metadata_load_mode: MetadataLoadMode = MetadataLoadMode.HEADER):
        super().__init__(file_paths=file_paths, zip_file=zip_file, metadata_load_mode=metadata_load_mode)

    def __getitem__(self, idx: int) -> TrainingInputData:
        with torch.no_grad():
            field, metadata = super().__getitem__(idx)
            assert isinstance(field, CartesianRadiationField), "Dataset must contain CartesianRadiationFields."
            assert isinstance(metadata, RadiationFieldMetadataV1), "Metadata must be of type RadiationFieldMetadataV1."

            rad_field = RadiationField(
                scatter_field=RadiationFieldChannel(
                    spectrum=RadiationFieldHelper.load_tensor_from_field(field, "scatter_field", "spectrum"),
                    fluence=RadiationFieldHelper.load_tensor_from_field(field, "scatter_field", "hits"),
                    error=RadiationFieldHelper.load_tensor_from_field(field, "scatter_field", "error")
                ),
                xray_beam= RadiationFieldChannel(
                    spectrum=RadiationFieldHelper.load_tensor_from_field(field, "xray_beam", "spectrum"),
                    fluence=RadiationFieldHelper.load_tensor_from_field(field, "xray_beam", "hits"),
                    error=RadiationFieldHelper.load_tensor_from_field(field, "xray_beam", "error")
                )
            )

            metadata_header = metadata.get_header()
            abc = (
                metadata_header.simulation.tube.radiation_direction.x,
                metadata_header.simulation.tube.radiation_direction.y,
                metadata_header.simulation.tube.radiation_direction.z
            )
            tube_direction = torch.tensor([abc[0], abc[1], abc[2]], dtype=torch.float32)
            tube_spectrum_data: HistogramVoxel = metadata.get_dynamic_metadata("tube_spectrum")
            tube_spectrum = torch.zeros((tube_spectrum_data.get_bins(), 2), dtype=torch.float32)
            tube_spectrum[:, 0] = torch.arange(0, tube_spectrum_data.get_bins() * tube_spectrum_data.get_histogram_bin_width(), tube_spectrum_data.get_histogram_bin_width(), dtype=torch.float32)
            tube_spectrum[:, 1] = torch.tensor(tube_spectrum_data.get_histogram(), dtype=torch.float32)
            tube_spectrum = tube_spectrum[:, 1]
            tube_spectrum = torch.where(~torch.isnan(tube_spectrum), tube_spectrum, 0.0)
            tube_spectrum = tube_spectrum / tube_spectrum.sum()

            input = DirectionalInput(
                direction=tube_direction,
                spectrum=tube_spectrum
            )

            return TrainingInputData(
                input=input,
                ground_truth=rad_field
            )


class RadField3DVoxelwiseDataset(RadField3DDataset):
    """
    A dataset for radiation fields generated with the RadField3D generator that loads single voxels.
    This dataset is a subclass of RadField3DDataset and interates a RadField3D datasets per voxel.
    It provides methods to access radiation fields and their metadata, and provides a method to access the radiation field data as PyTorch tensors.
    The dataset returns instances of TrainingInputData, which contains the input as a PositionalInput as well as the ground truth as a RadiationField.
    The shape of the ground truth tensors is (c, x, y, z) c is the number of channels (typically 32 for spectra and 1 for all other layers), and (x, y, z) are the dimensions of the radiation field.
    The shape of the input tensor is (3,) for the voxel position in normalized world space [0..1] as well as the tube direction and (n,) for the tube spectrum, where n is the number of bins in the tube spectrum.
    """

    def __init__(self, file_paths: list[str] = None, zip_file: str = None, metadata_load_mode: MetadataLoadMode = MetadataLoadMode.HEADER):
        super().__init__(file_paths=file_paths, zip_file=zip_file, metadata_load_mode=metadata_load_mode)
        field = self._get_field(0)
        self.field_voxel_counts = field.get_voxel_counts()
        self.voxels_per_field = self.field_voxel_counts.x * self.field_voxel_counts.y * self.field_voxel_counts.z
        self.cached_metadata: DirectionalInput = None
        self.cached_fields: RadiationField = None

    def prefetch_data(self):
        """
        Prefetches all data in the dataset to speed up training.
        This method loads all radiation fields and their metadata into memory.
        """
        if self.cached_metadata is not None and self.cached_fields is not None:
            raise RuntimeError("Data has already been prefetched. Please create a new dataset instance to reload the data.")
        if len(self.file_paths) == 0:
            raise RuntimeError("No files found in the dataset. Please check the file paths or zip file.")
        first_data = super().__getitem__(0)
        with torch.no_grad():
            field_voxel_counts = first_data.ground_truth.scatter_field.spectrum.shape[1:4]
            self.cached_metadata = DirectionalInput(
                direction=torch.empty((len(self.file_paths), 3), dtype=torch.float32).share_memory_(),
                spectrum=torch.empty((len(self.file_paths), first_data.input.spectrum.shape[0]), dtype=torch.float32).share_memory_()
            )

            self.cached_fields = RadiationField(
                scatter_field=RadiationFieldChannel(
                    spectrum=torch.empty((len(self.file_paths), first_data.input.spectrum.shape[0], *field_voxel_counts), dtype=torch.float32).share_memory_(),
                    fluence=torch.empty((len(self.file_paths), 1, *field_voxel_counts), dtype=torch.float32).share_memory_(),
                    error=torch.empty((len(self.file_paths), 1, *field_voxel_counts), dtype=torch.float32).share_memory_()
                ),
                xray_beam=RadiationFieldChannel(
                    spectrum=torch.empty((len(self.file_paths), first_data.input.spectrum.shape[0], *field_voxel_counts), dtype=torch.float32).share_memory_(),
                    fluence=torch.empty((len(self.file_paths), 1, *field_voxel_counts), dtype=torch.float32).share_memory_(),
                    error=torch.empty((len(self.file_paths), 1, *field_voxel_counts), dtype=torch.float32).share_memory_()
                )
            )


            for i in range(len(self.file_paths)):
                data = super().__getitem__(i)
                self.cached_metadata.direction[i] = data.input.direction.detach()
                self.cached_metadata.spectrum[i] = data.input.spectrum.detach()

                self.cached_fields.scatter_field.spectrum[i] = data.ground_truth.scatter_field.spectrum.detach()
                self.cached_fields.scatter_field.fluence[i] = data.ground_truth.scatter_field.fluence.detach()
                self.cached_fields.scatter_field.error[i] = data.ground_truth.scatter_field.error.detach()
                self.cached_fields.xray_beam.spectrum[i] = data.ground_truth.xray_beam.spectrum.detach()
                self.cached_fields.xray_beam.fluence[i] = data.ground_truth.xray_beam.fluence.detach()
                self.cached_fields.xray_beam.error[i] = data.ground_truth.xray_beam.error.detach()
            
            self.cached_metadata.direction.requires_grad_(False)
            self.cached_metadata.spectrum.requires_grad_(False)
            self.cached_fields.scatter_field.spectrum.requires_grad_(False)
            self.cached_fields.scatter_field.fluence.requires_grad_(False)
            self.cached_fields.scatter_field.error.requires_grad_(False)
            self.cached_fields.xray_beam.spectrum.requires_grad_(False)
            self.cached_fields.xray_beam.fluence.requires_grad_(False)
            self.cached_fields.xray_beam.error.requires_grad_(False)
                

    def __getitem__(self, idx: int) -> TrainingInputData:
        voxel_idx = idx % self.voxels_per_field
        file_idx = idx // self.voxels_per_field
        xyz = (
            voxel_idx % self.field_voxel_counts.x,
            (voxel_idx // self.field_voxel_counts.x) % self.field_voxel_counts.y,
            voxel_idx // (self.field_voxel_counts.x * self.field_voxel_counts.y)
        )
        xyz = torch.tensor([xyz[0], xyz[1], xyz[2]], dtype=torch.float32, requires_grad=False)
        xyz_idx = xyz.long()

        if self.cached_metadata is not None:
            field = RadiationField(
                scatter_field=RadiationFieldChannel(
                    spectrum=self.cached_fields.scatter_field.spectrum[file_idx, :, xyz_idx[0], xyz_idx[1], xyz_idx[2]].clone(),
                    fluence=self.cached_fields.scatter_field.fluence[file_idx, :, xyz_idx[0], xyz_idx[1], xyz_idx[2]].clone(),
                    error=self.cached_fields.scatter_field.error[file_idx, :, xyz_idx[0], xyz_idx[1], xyz_idx[2]].clone()
                ),
                xray_beam=RadiationFieldChannel(
                    spectrum=self.cached_fields.xray_beam.spectrum[file_idx, :, xyz_idx[0], xyz_idx[1], xyz_idx[2]].clone(),
                    fluence=self.cached_fields.xray_beam.fluence[file_idx, :, xyz_idx[0], xyz_idx[1], xyz_idx[2]].clone(),
                    error=self.cached_fields.xray_beam.error[file_idx, :, xyz_idx[0], xyz_idx[1], xyz_idx[2]].clone()
                )
            )
            # normalize xyz to 0 to 1
            field_voxel_counts = torch.tensor([self.field_voxel_counts.x, self.field_voxel_counts.y, self.field_voxel_counts.z], dtype=torch.float32, device=xyz.device, requires_grad=False)
            xyz = xyz / (field_voxel_counts - 1.0) # Normalize xyz to [0, 1]

            input = PositionalInput(
                position=xyz,
                direction=self.cached_metadata.direction[file_idx].clone(),
                spectrum=self.cached_metadata.spectrum[file_idx].clone()
            )

            return TrainingInputData(
                input=input,
                ground_truth=field
            )
        else:
            scatter_spectrum = self._get_voxel_flat(file_idx=file_idx, vx_idx=voxel_idx, channel_name="scatter_field", layer_name="spectrum").get_histogram()
            scatter_fluence = self._get_voxel_flat(file_idx=file_idx, vx_idx=voxel_idx, channel_name="scatter_field", layer_name="hits").get_data()
            scatter_error = self._get_voxel_flat(file_idx=file_idx, vx_idx=voxel_idx, channel_name="scatter_field", layer_name="error").get_data()
            xray_spectrum = self._get_voxel_flat(file_idx=file_idx, vx_idx=voxel_idx, channel_name="xray_beam", layer_name="spectrum").get_histogram()
            xray_fluence = self._get_voxel_flat(file_idx=file_idx, vx_idx=voxel_idx, channel_name="xray_beam", layer_name="hits").get_data()
            xray_error = self._get_voxel_flat(file_idx=file_idx, vx_idx=voxel_idx, channel_name="xray_beam", layer_name="error").get_data()
            field = RadiationField(
                scatter_field=RadiationFieldChannel(
                    spectrum=torch.tensor(scatter_spectrum, dtype=torch.float32, device=xyz.device, requires_grad=False),
                    fluence=torch.tensor(scatter_fluence, dtype=torch.float32, device=xyz.device, requires_grad=False),
                    error=torch.tensor(scatter_error, dtype=torch.float32, device=xyz.device, requires_grad=False)
                ),
                xray_beam=RadiationFieldChannel(
                    spectrum=torch.tensor(xray_spectrum, dtype=torch.float32, device=xyz.device, requires_grad=False),
                    fluence=torch.tensor(xray_fluence, dtype=torch.float32, device=xyz.device, requires_grad=False),
                    error=torch.tensor(xray_error, dtype=torch.float32, device=xyz.device, requires_grad=False)
                )
            )
            metadata = self._get_metadata(file_idx)
            metadata_header = metadata.get_header()
            abc = (
                metadata_header.simulation.tube.radiation_direction.x,
                metadata_header.simulation.tube.radiation_direction.y,
                metadata_header.simulation.tube.radiation_direction.z
            )
            tube_direction = torch.tensor([abc[0], abc[1], abc[2]], dtype=torch.float32, device=xyz.device, requires_grad=False)
            tube_spectrum_data: HistogramVoxel = metadata.get_dynamic_metadata("tube_spectrum")
            tube_spectrum = torch.zeros((tube_spectrum_data.get_bins(), 2), dtype=torch.float32, device=xyz.device, requires_grad=False)
            tube_spectrum[:, 0] = torch.arange(0, tube_spectrum_data.get_bins() * tube_spectrum_data.get_histogram_bin_width(), tube_spectrum_data.get_histogram_bin_width(), dtype=torch.float32, device=xyz.device)
            tube_spectrum[:, 1] = torch.tensor(tube_spectrum_data.get_histogram(), dtype=torch.float32, device=xyz.device, requires_grad=False)
            tube_spectrum = tube_spectrum[:, 1]
            tube_spectrum = torch.where(~torch.isnan(tube_spectrum), tube_spectrum, 0.0)
            tube_spectrum = tube_spectrum / tube_spectrum.sum()

            field_voxel_counts = torch.tensor([self.field_voxel_counts.x, self.field_voxel_counts.y, self.field_voxel_counts.z], dtype=torch.float32, device=xyz.device, requires_grad=False)
            xyz = xyz / (field_voxel_counts - 1.0) # Normalize xyz to [0, 1]

            input = PositionalInput(
                position=xyz,
                direction=tube_direction,
                spectrum=tube_spectrum
            )
            return TrainingInputData(
                input=input,
                ground_truth=field
            )

    def __len__(self):
        return super().__len__() * self.voxels_per_field

    def __getitems__(self, indices) -> Union[TrainingInputData, list[TrainingInputData]]:
        if self.cached_metadata is not None and self.cached_fields is not None:
            indices = torch.tensor(indices, dtype=torch.int64, device=self.cached_fields.scatter_field.fluence.device, requires_grad=False) if not isinstance(indices, Tensor) else indices
            file_indices = indices // self.voxels_per_field
            voxel_indices = indices % self.voxels_per_field
            xyz = torch.empty((len(indices), 3), dtype=torch.float32, requires_grad=False, device=indices.device)
            voxel_field_counts = torch.tensor([self.field_voxel_counts.x, self.field_voxel_counts.y, self.field_voxel_counts.z], dtype=torch.float32, device=indices.device, requires_grad=False)
            xyz[:, 0] = voxel_indices % self.field_voxel_counts.x
            xyz[:, 1] = (voxel_indices // self.field_voxel_counts.x) % self.field_voxel_counts.y
            xyz[:, 2] = voxel_indices // (self.field_voxel_counts.x * self.field_voxel_counts.y)

            spectra_scatter = self.cached_fields.scatter_field.spectrum[file_indices, :, xyz[:, 0].long(), xyz[:, 1].long(), xyz[:, 2].long()].clone()
            spectra_beam = self.cached_fields.xray_beam.spectrum[file_indices, :, xyz[:, 0].long(), xyz[:, 1].long(), xyz[:, 2].long()].clone()
            fluence_scatter = self.cached_fields.scatter_field.fluence[file_indices, :, xyz[:, 0].long(), xyz[:, 1].long(), xyz[:, 2].long()].clone()
            fluence_beam = self.cached_fields.xray_beam.fluence[file_indices, :, xyz[:, 0].long(), xyz[:, 1].long(), xyz[:, 2].long()].clone()
            error_scatter = self.cached_fields.scatter_field.error[file_indices, :, xyz[:, 0].long(), xyz[:, 1].long(), xyz[:, 2].long()].clone()
            error_beam = self.cached_fields.xray_beam.error[file_indices, :, xyz[:, 0].long(), xyz[:, 1].long(), xyz[:, 2].long()].clone()

            xyz = xyz / (voxel_field_counts - 1.0) # Normalize xyz to [0, 1]

            inputs = PositionalInput(
                position=xyz,
                direction=self.cached_metadata.direction[file_indices].clone(),
                spectrum=self.cached_metadata.spectrum[file_indices].clone()
            )

            fields = RadiationField(
                scatter_field=RadiationFieldChannel(
                    spectrum=spectra_scatter,
                    fluence=fluence_scatter,
                    error=error_scatter
                ),
                xray_beam=RadiationFieldChannel(
                    spectrum=spectra_beam,
                    fluence=fluence_beam,
                    error=error_beam
                )
            )
            training_data = TrainingInputData(input=inputs, ground_truth=fields)
            return training_data
        else:
            return super().__getitems__(indices)
