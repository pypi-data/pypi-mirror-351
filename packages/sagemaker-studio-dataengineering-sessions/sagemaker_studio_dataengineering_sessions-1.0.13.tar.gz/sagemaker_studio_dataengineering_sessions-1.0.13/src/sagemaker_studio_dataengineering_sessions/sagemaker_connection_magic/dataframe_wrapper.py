from IPython import get_ipython
import pandas as pd

from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.sagemaker_connection_display import SageMakerConnectionDisplay
from sagemaker_studio_dataengineering_sessions.sagemaker_connection_magic.sagemaker_display_magic.display_compute import DisplayMagicCompute
from sagemaker_studio_dataengineering_sessions.sagemaker_connection_magic.sagemaker_display_magic.display_render import DisplayMagicRender


class DataFrameWrapper:
    def __init__(self, custom_display: DisplayMagicRender, **kwargs):
        self.custom_display = custom_display
        self.df = None
        display_compute_object = get_ipython().user_ns[custom_display.display_magic_compute]
        if isinstance(display_compute_object, DisplayMagicCompute):
            self.df = display_compute_object.df
        # file_list is the list of S3 paths in which the data is stored
        # once the work to automatically unload query results is complete
        file_list = kwargs.get("file_list")
        if file_list is not None:
            self._file_list = file_list

    def _ipython_display_(self):
        self.custom_display.render()

    def to_pandas(self):
        if isinstance(self.df, pd.DataFrame):
            return self.df
        else:
            SageMakerConnectionDisplay.write_msg(f"Cannot convert DataFrame of type '{type(self.df).__name__}' to a pandas DataFrame.")
