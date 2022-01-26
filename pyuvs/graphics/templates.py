"""The :code:`templates` module provides templates for creating graphics."""

import matplotlib.pyplot as plt
from pyuvs.constants import angular_slit_width, minimum_mirror_angle, \
    maximum_mirror_angle


class SegmentDetectorImage:
    def __init__(self, n_swaths: int, height: float):
        """Make a template of a detector image containing all data from a
        segment. This is broadcast into angular space so that the pixels are
        not warped. The data axis spans the figure.

        Parameters
        ----------
        n_swaths
            The number of swaths present in the data.
        height
            The desired figure height [inches].

        """
        self._n_swaths = n_swaths
        self._height = height
        self._width = self._compute_width()

        self._figure = self._setup_figure()

        self._data_axis = self._add_data_axis()

    def _compute_width(self) -> float:
        aspect_ratio = self._n_swaths * angular_slit_width / \
                       (maximum_mirror_angle - minimum_mirror_angle)
        return aspect_ratio * self._height

    def _setup_figure(self) -> plt.Figure:
        return plt.figure(figsize=(self._width, self._height))

    def _add_data_axis(self) -> plt.Axes:
        return self._figure.add_axes([0, 0, 1, 1])

    @property
    def figure(self) -> plt.Figure:
        """Get the figure.

        Returns
        -------
        plt.Figure
            The figure.

        """
        return self._figure

    @property
    def data_axis(self) -> plt.Axes:
        """Get the data axis, which spans the entire figure.

        Returns
        -------
        plt.Axes
            The data axis.
        """
        return self._data_axis


class ApoapseMUVQuicklook:
    def __init__(self, width: float = 8.25, height: float = 11.75):
        self._width = width
        self._height = height
        self._axis_aspect_ratio = 1.5
        self._border_thickness = 0.025
        self._banner_height = 0.15
        self._axis_width = 0.5 - self._border_thickness * 1.5
        self._axis_height = self._axis_width * self._width / self._axis_aspect_ratio / self._height

        self._figure = self._setup_figure()

        self._banner_axis = self._add_banner_axis()

        self._no_data_axis = self._add_no_data_axis()
        self._aurora_data_axis = self._add_aurora_data_axis()

        self._no_map_axis = self._add_no_map_axis()
        self._aurora_map_axis = self._add_aurora_map_axis()

        self._no_data_globe_axis = self._add_no_data_globe_axis()
        self._no_map_globe_axis = self._add_no_map_globe_axis()
        self._aurora_data_globe_axis = self._add_aurora_data_globe_axis()
        self._aurora_map_globe_axis = self._add_aurora_map_globe_axis()

        self._solar_zenith_angle_axis = self._add_solar_zenith_angle_axis()
        self._emission_angle_axis = self._add_emission_angle_axis()

    def _setup_figure(self):
        self._set_quicklook_rc_params()
        return plt.figure(figsize=(self._width, self._height))

    @staticmethod
    def _set_quicklook_rc_params() -> None:
        plt.rc('pdf', fonttype=42)
        plt.rc('ps', fonttype=42)

        plt.rc('font', **{'family': 'STIXGeneral'})
        plt.rc('mathtext', fontset='stix')
        plt.rc('text', usetex=False)

        plt_thick = 0.5
        plt.rc('lines', linewidth=plt_thick)
        plt.rc('axes', linewidth=plt_thick)

    def _add_banner_axis(self) -> plt.Axes:
        return self.figure.add_axes(
            [self._border_thickness, 1 -
             self._border_thickness - self._banner_height,
             1 - 2 * self._border_thickness,
             self._banner_height])

    def _compute_large_axis_figure_height(self, row: int) -> float:
        # Row starts from 0 and goes top down
        return 1 - self._banner_height - self._axis_height * (row + 1) - \
               self._border_thickness * (row + 2)

    def _compute_globe_height(self) -> float:
        return 2 * self._border_thickness + self._axis_height / 2

    def _add_no_data_axis(self) -> plt.Axes:
        height = self._compute_large_axis_figure_height(0)
        return self.figure.add_axes([self._border_thickness, height,
                                     self._axis_width, self._axis_height])

    def _add_aurora_data_axis(self) -> plt.Axes:
        height = self._compute_large_axis_figure_height(0)
        return self.figure.add_axes([0.5 + self._border_thickness / 2, height,
                                     self._axis_width, self._axis_height])

    def _add_no_map_axis(self) -> plt.Axes:
        height = self._compute_large_axis_figure_height(1)
        return self.figure.add_axes([self._border_thickness, height,
                                     self._axis_width, self._axis_height])

    def _add_aurora_map_axis(self) -> plt.Axes:
        height = self._compute_large_axis_figure_height(1)
        return self.figure.add_axes([0.5 + self._border_thickness / 2, height,
                                     self._axis_width, self._axis_height])

    def _add_no_data_globe_axis(self) -> plt.Axes:
        height = self._compute_globe_height()
        return self.figure.add_axes([self._border_thickness, height,
                                     self._axis_width/2, self._axis_height/2])

    def _add_no_map_globe_axis(self) -> plt.Axes:
        height = self._compute_globe_height()
        return self.figure.add_axes([self._border_thickness + self._axis_width/2, height,
                                     self._axis_width/2, self._axis_height/2])

    def _add_aurora_data_globe_axis(self) -> plt.Axes:
        height = self._compute_globe_height()
        return self.figure.add_axes([0.5 + self._border_thickness / 2, height,
                                     self._axis_width/2, self._axis_height/2])

    def _add_aurora_map_globe_axis(self) -> plt.Axes:
        height = self._compute_globe_height()
        return self.figure.add_axes([0.5 + self._border_thickness / 2 + self._axis_width / 2, height,
                                     self._axis_width/2, self._axis_height/2])

    def _make_angle_width(self) -> float:
        return (0.5 - self._border_thickness * 2.5) / 2

    def _add_solar_zenith_angle_axis(self) -> plt.Axes:
        width = self._make_angle_width()
        return self.figure.add_axes([self._border_thickness, self._border_thickness, width, self._axis_height / 2])

    def _add_emission_angle_axis(self) -> plt.Axes:
        width = self._make_angle_width()
        return self.figure.add_axes([self._border_thickness * 2 + width, self._border_thickness, width, self._axis_height / 2])

    @property
    def figure(self) -> plt.Figure:
        return self._figure

    @property
    def no_data_axis(self) -> plt.Axes:
        return self._no_data_axis





# Reposition sub axes
# Add blank colorbars
class StandardApoapseQuicklook:
    """Create the template of a standard apoapse quicklook.

    This template has a 2.5% boarder around the image and thus the axes span
    95% of the width. There is also a 2.5% spacing between axes. The "banner"
    spans 12.5% of the height. The large axes span 30% of the height each
    whereas the smaller axes span 15% of the height.

    Parameters
    ----------
    width
        The width of the graphic [inches].
    height
        The height of the graphic [inches].

    Notes
    -----
    The template can be seen below (click the png to see borders).

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
        self.top_large_axis = self._add_top_large_axis()
        self.bottom_large_axis = self._add_bottom_large_axis()
        self.left_small_axis = self._add_left_small_axis()
        self.right_small_axis = self._add_right_small_axis()

        self._turn_off_axes_ticks()

    def _setup_figure(self) -> plt.Figure:
        #plt.style.use(Path(__file__).parent.joinpath('rcparams.mplstyle'))
        return plt.figure(figsize=(self.width, self.height))

    def _add_banner_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.85, 0.95, 0.125])

    def _add_top_large_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.525, 0.95, 0.3])

    def _add_bottom_large_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.2, 0.95, 0.3])

    def _add_left_small_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.025, 0.025, 0.35, 0.15])

    def _add_right_small_axis(self) -> plt.Axes:
        return self.fig.add_axes([0.525, 0.025, 0.35, 0.15])

    def _turn_off_axes_ticks(self):
        self._turn_off_ticks(self.banner_axis)
        self._turn_off_ticks(self.top_large_axis)
        self._turn_off_ticks(self.bottom_large_axis)
        self._turn_off_ticks(self.left_small_axis)
        self._turn_off_ticks(self.right_small_axis)

    @staticmethod
    def _turn_off_ticks(ax: plt.Axes) -> None:
        ax.set_xticks([])
        ax.set_yticks([])


if __name__ == '__main__':
    #ql = StandardApoapseQuicklook()
    #plt.savefig('/home/kyle/test.pdf')

    amq = ApoapseMUVQuicklook()
    plt.savefig('/home/kyle/ql_testing/test.pdf')
