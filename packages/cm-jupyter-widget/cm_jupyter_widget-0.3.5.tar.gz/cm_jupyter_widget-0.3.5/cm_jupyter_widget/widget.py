import anywidget
import traitlets
from traitlets import observe
import pathlib
import json
from typing import Union, Dict, Any

class CleverMapsWidget(anywidget.AnyWidget):
    
    _esm = pathlib.Path(__file__).parent / "index.js"
    _css = pathlib.Path(__file__).parent / "index.css"

    # required
    view_url = traitlets.Unicode(allow_none=False).tag(sync=True)
    # optional
    base_url = traitlets.Unicode(default_value='https://secure.clevermaps.io/').tag(sync=True)
    options = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    width = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    height = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)
    add_filter_callback = traitlets.Any(default_value=None, allow_none=True).tag(sync=True)
    filter_added = traitlets.Dict({}).tag(sync=True)

    command = traitlets.Dict({}).tag(sync=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'options' in kwargs and isinstance(kwargs['options'], dict):
            self.options = json.dumps(kwargs['options'])

    def toggle_fit_all(self):
        """Fit all features in the view"""
        self.command = {"type": "toggleFitAll"}

    def add_filter(self, definition_id: str, values: Dict[str, Any], instance_id: str):
        """Add a filter
        
        Args:
            definition_id (str): The ID of the filter definition
            values: The values to set the filter to, depending on filter type:
                - MultiSelect: {"values": ["Male", 1, null]}
                - SingleSelect: {"value": "selected_value"} or {"value": null}
                - Feature: {"values": ["feature1", 1]} or {"values": null}
                - Histogram: {"values": [1, 10], "nullFiltered": true} or {"values": [null, null]}
                - Date: {
                    "startDate": {"value": "2023-01-01"} or date function,
                    "endDate": {"value": "2023-12-31"} or date function
                  }
                - Indicator: {"values": [min, max], "granularity": "year"}
            instance_id (str): The instance ID of the filter
        """
        self.command = {
            "type": "addFilter",
            "definitionId": definition_id,
            "values": values,
            "instanceId": instance_id
        }

    def set_filter(self, instance_id: str, value):
        """Set a filter value
        
        Args:
            instance_id (str): The instance ID of the filter to set
            value: The value to set the filter to
        """
        self.command = {
            "type": "setFilter",
            "instanceId": instance_id,
            "value": value
        }

    def remove_filter(self, instance_id: str):
        """Remove a filter
        
        Args:
            instance_id (str): The instance ID of the filter to remove
        """
        self.command = {
            "type": "removeFilter",
            "instanceId": instance_id
        }

    def reset_filter(self, instance_id: str):
        """Reset a filter
        
        Args:
            instance_id (str): The instance ID of the filter to reset
        """
        self.command = {
            "type": "resetFilter",
            "instanceId": instance_id
        }

    def set_state(self, view_url):
        """Set the state by loading a new view URL
        
        Args:
            view_url (str): The URL of the view to load
        """
        self.command = {
            "type": "setState",
            "viewUrl": view_url
        }

    def open_bookmark_modal(self):
        """Open the bookmark modal"""
        self.command = {
            "type": "openBookmarkModal"
        }

    def open_export_modal(self):
        """Open the export modal"""
        self.command = {
            "type": "openExportModal"
        }

    @observe('filter_added')
    def _handle_filter_added(self, change):
        if self.add_filter_callback is not None:
            self.add_filter_callback()