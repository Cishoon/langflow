from lfx.custom.custom_component.component import Component


class ImageComponent(Component):
    display_name = "Image Component"
    description = "Base class for components that produce or consume images."

    @staticmethod
    def normalize_files(files):
        """Ensure files is a list and drop falsy entries."""
        if not files:
            return []
        if not isinstance(files, list):
            files = [files]
        return [f for f in files if f]
