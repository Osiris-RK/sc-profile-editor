"""
Graphic exporter for annotated device images
"""

from typing import Dict
from PIL import Image


class GraphicExporter:
    """Export annotated device graphics"""

    def __init__(self, profile_data: Dict):
        self.profile_data = profile_data

    def export(self, output_path: str):
        """Export annotated device graphic"""
        # TODO: Implement graphic export
        pass
