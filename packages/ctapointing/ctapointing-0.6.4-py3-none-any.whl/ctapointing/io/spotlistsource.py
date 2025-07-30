import tables

from ctapipe.core import Provenance
from ctapipe.core.component import Component
from ctapipe.core.traits import Int, Path, Undefined
from ctapipe.io import HDF5TableReader


class SpotListSource(Component):
    """
    Class to read SpotList objects from HDF5 input file.
    """

    input_url = Path(help="Path to the input file containing spotlists.").tag(
        config=True
    )

    max_events = Int(
        None,
        allow_none=True,
        help="Maximum number of events that will be read from the file",
    ).tag(config=True)

    def __init__(self, input_url=None, config=None, parent=None, **kwargs):
        """
        Class to read SpotList objects from HDF5 input file.
        For now a very much simplified version of the ctapipe.io.HDF5EventSource class.

        Parameters
        ----------
        input_url : str
            Path of the file to load
        config : traitlets.loader.Config
            Configuration specified by config file or cmdline arguments.
            Used to set traitlet values.
            Set to None if no configuration to pass.
        parent:
            Parent from which the config is used. Mutually exclusive with config
        kwargs
        """
        # traitlets differentiates between not getting the kwarg
        # and getting the kwarg with a None value.
        # the latter overrides the value in the config with None, the former
        # enables getting it from the config.
        if input_url not in {None, Undefined}:
            kwargs["input_url"] = input_url

        super().__init__(config=config, parent=parent, **kwargs)

        self.log.info(f"INPUT PATH = {self.input_url}")

        if self.max_events:
            self.log.info(f"Max events being read = {self.max_events}")

        Provenance().add_input_file(str(self.input_url), role="spotlist")

        self.file_ = tables.open_file(self.input_url)

    @staticmethod
    def is_compatible(file_path):
        path = Path(file_path).expanduser()
        if not path.is_file():
            return False

        with path.open("rb") as f:
            magic_number = f.read(8)

        if magic_number != b"\x89HDF\r\n\x1a\n":
            return False

        return True

    @property
    def is_stream(self):
        return False

    def __len__(self):
        n_events = len(self.file_.list_nodes("/spots"))
        if self.max_events is not None:
            return min(n_events, self.max_events)
        return n_events

    def __iter__(self):
        """
        Iterate over SpotList tables

        """
        # avoid circular import
        from ctapointing.imagesolver import SpotList

        # determine list of spotlist tables
        nodes = self.file_.list_nodes("/spots")

        self.reader = HDF5TableReader(self.file_)

        n_read = 0
        for node in nodes:
            spotlist = next(
                HDF5TableReader(self.file_).read(
                    "/spots/" + node.name,
                    SpotList,
                )
            )
            n_read += 1

            yield spotlist
            if self.max_events and n_read >= self.max_events:
                break

    def __enter__(self):
        return self

    @classmethod
    def from_url(cls, input_url, **kwargs):
        return cls(input_url=input_url, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.file_.close()
