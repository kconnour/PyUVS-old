"""The graphics module provides graphics for graphics."""


from pathlib import Path
import matplotlib.pyplot as plt


class Plain:
    pass


class ExtendedApoapseQuicklook:
    pass


# Add colorbars
class StandardApoapseQuicklook:
    """Create a template of the standard apoapse quicklook.

    Parameters
    ----------
    width
        The width of the graphic [inches].
    height
        The height of the graphic [inches].

    Notes
    -----
    The template can be seen below.

    .. plot::

      import matplotlib.pyplot as plt
      from pyuvs.graphics.templates import StandardApoapseQuicklook
      saq = StandardApoapseQuicklook()
      plt.show()

    """
    def __init__(self, width: float = 6, height: float = 9):

        self.width = width
        self.height = height

        self.fig = self._setup_figure()

        self.banner_axis = self._add_banner_axis()
        self.data_axis = self._add_data_axis()
        self.geometry_axis = self._add_geometry_axis()
        self.solar_zenith_angle_axis = self._add_solar_zenith_angle_axis()
        self.local_time_axis = self._add_local_time_axis()

        self._turn_off_axes_ticks()

    def _setup_figure(self) -> plt.Figure:
        plt.style.use(Path(__file__).parent.joinpath('rcparams.mplstyle'))
        return plt.figure(figsize=(self.width, self.height))

    def _add_banner_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.85, 0.95, 0.125])

    def _add_data_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.525, 0.95, 0.3])

    def _add_geometry_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.2, 0.95, 0.3])

    def _add_solar_zenith_angle_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.025, 0.35, 0.15])

    def _add_local_time_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.525, 0.025, 0.35, 0.15])

    def _turn_off_axes_ticks(self):
        self._turn_off_ticks(self.banner_axis)
        self._turn_off_ticks(self.data_axis)
        self._turn_off_ticks(self.geometry_axis)
        self._turn_off_ticks(self.solar_zenith_angle_axis)
        self._turn_off_ticks(self.local_time_axis)

    @staticmethod
    def _turn_off_ticks(ax) -> None:
        ax.set_xticks([])
        ax.set_yticks([])


if __name__ == '__main__':
    ql = StandardApoapseQuicklook()
    plt.savefig('/home/kyle/test.pdf')
