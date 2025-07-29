from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class Breeam4b(Function):
    """Calculate credits for BREEAM 4b."""

    folder = Inputs.folder(
        description='This folder is an output folder of annual daylight recipe. Folder '
        'should include grids_info.json and sun-up-hours.txt. The command uses the list '
        'in grids_info.json to find the result files for each sensor grid.',
        path='results'
    )

    model = Inputs.file(
        description='Path to HBJSON file. The purpose of the model in this function is '
        'to use the mesh area of the sensor grids to calculate area-weighted metrics. '
        'In case no model is provided or the sensor grids in the model do not have any '
        'mesh area, it will be assumed that all sensor points cover the same area.',
        path='model.hbjson', optional=True
    )

    grid_filter = Inputs.str(
        description='Text for a grid identifier or a pattern to filter the sensor grids '
        'of the model that are simulated. For instance, first_floor_* will simulate '
        'only the sensor grids that have an identifier that starts with '
        'first_floor_. By default, all grids in the model will be simulated.',
        default='*'
    )

    @command
    def breeam_daylight_4b(self):
        return 'honeybee-radiance-postprocess post-process breeam breeam-4b ' \
            'results --model-file model.hbjson --grids-filter " {{self.grid_filter}} " ' \
            '--sub-folder breeam_summary'

    # outputs
    breeam_summary = Outputs.folder(
        description='BREEAM summary folder.',
        path='breeam_summary'
    )


@dataclass
class Breeam4bVisMetadata(Function):
    """Create visualization metadata files for BREEAM 4b."""

    output_folder = Inputs.str(
        description='Name of the output folder.', default='visualization',
        path='visualization'
    )

    @command
    def create_breeam_daylight_4b_vis_data(self):
        return 'honeybee-radiance-postprocess post-process breeam breeam-4b-vis-metadata ' \
            '--output-folder "{{self.output_folder}}"'

    # outputs
    vis_metadata_folder = Outputs.folder(
        description='Output folder with visualization metadata files.',
        path='visualization'
    )
