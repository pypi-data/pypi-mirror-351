import anywidget
import traitlets
import pathlib

class CleverMapsWidget(anywidget.AnyWidget):
    
    _esm = pathlib.Path(__file__).parent / "index.js"
    _css = pathlib.Path(__file__).parent / "index.css"

    # required
    view_url = traitlets.Unicode(allow_none=False).tag(sync=True)
    # optional
    options = traitlets.Dict(allow_none=True).tag(sync=True)