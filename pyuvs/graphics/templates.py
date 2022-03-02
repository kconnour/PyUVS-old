"""This module provides templates for creating graphics."""

from pathlib import Path
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pyuvs.constants import angular_slit_width, minimum_mirror_angle, \
    maximum_mirror_angle


# TODO: this renders oddly online..
class SegmentDetectorImage:
    """Make a template of a detector image containing all data from a
    segment. This is broadcast into angular space so that the pixels are
    not warped. The data axis spans the figure.

    Parameters
    ----------
    n_swaths
        The number of swaths present in the data.
    height
        The desired figure height [inches].

    Examples
    --------
    Visualize this template.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       from pyuvs.graphics.templates import SegmentDetectorImage

       SegmentDetectorImage(6, 4)
       plt.show()

    """
    def __init__(self, n_swaths: int, height: float):
        self._n_swaths = n_swaths
        self._height = height
        self._width = self._compute_width()

        self._figure = self._setup_figure()

        self._data_axis = self._add_data_axis()

    def _compute_width(self) -> float:
        aspect_ratio = self._n_swaths * angular_slit_width / \
                       (2 * (maximum_mirror_angle - minimum_mirror_angle))
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
    """A class that creates a blank apoapse MUV quicklook.

    Parameters
    ----------
    figure_width: float
        The desired output figure width.

    Notes
    -----
    The figure width can theoretically be any value, but values less than
    14 will compress the text in such a way that it's unreadable.

    Examples
    --------
    Visualize this template.

    .. plot::
       :include-source:

       import matplotlib.pyplot as plt
       from pyuvs.graphics.templates import ApoapseMUVQuicklook

       ApoapseMUVQuicklook()
       plt.show()

    """
    def __init__(self, figure_width: float = 14):

        self._figure = self._make_figure(figure_width)

        self._gridspec = self._make_gridspecs()

        self._text_axes = self._make_text_axes()
        self._data_axes = self._make_data_axes()
        self._map_axes = self._make_map_axes()
        self._angle_axes = self._make_angle_axes()

        self._color_maps = {}
        self._norms = {}

        self._add_colorbars()

        del self._gridspec

    def _make_figure(self, figure_width: float) -> plt.Figure:
        self._set_rc_params()
        return plt.figure(figsize=(figure_width, figure_width * 9 / 16),
                          constrained_layout=True,
                          dpi=100)

    @staticmethod
    def _set_rc_params() -> None:
        rc = Path(__file__).parent.resolve() / 'apoapse_muv_quicklook.mplstyle'
        plt.style.use(rc)

    def _make_gridspecs(self) -> dict:
        row_gridspec = gridspec.GridSpec(7, 1, figure=self._figure)
        text_gridspec = gridspec.GridSpecFromSubplotSpec(
            1, 3, subplot_spec=row_gridspec[0])
        data_gridspec = gridspec.GridSpecFromSubplotSpec(
            2, 6,
            subplot_spec=row_gridspec[1:5],
            width_ratios=[4, 2, 0.125, 4, 2, 0.125])
        angle_gridspec = gridspec.GridSpecFromSubplotSpec(
            2, 4,
            subplot_spec=row_gridspec[5:],
            height_ratios=[12, 1])
        return {'text': text_gridspec,
                'data': data_gridspec,
                'angle': angle_gridspec}

    def _make_text_axes(self) -> dict:
        text_gridspec = self._gridspec['text']
        left_text_axis = self._figure.add_subplot(text_gridspec[0])
        center_text_axis = self._figure.add_subplot(text_gridspec[1])
        right_text_axis = self._figure.add_subplot(text_gridspec[2])
        return {'left': left_text_axis,
                'center': center_text_axis,
                'right': right_text_axis}

    def _make_data_axes(self) -> dict:
        data_gridspec = self._gridspec['data']
        no_swath_axis = self._figure.add_subplot(data_gridspec[0, 0])
        no_globe_axis = self._figure.add_subplot(data_gridspec[0, 1])
        aurora_swath_axis = self._figure.add_subplot(data_gridspec[0, 3])
        aurora_globe_axis = self._figure.add_subplot(data_gridspec[0, 4])

        no_globe_axis.set_aspect('equal')
        aurora_globe_axis.set_aspect('equal')

        return {'no_swath': no_swath_axis,
                'no_globe': no_globe_axis,
                'aurora_swath': aurora_swath_axis,
                'aurora_globe': aurora_globe_axis}

    def _make_map_axes(self) -> dict:
        data_gridspec = self._gridspec['data']
        surface_map_swath_axis = self._figure.add_subplot(data_gridspec[1, 0])
        surface_map_globe_axis = self._figure.add_subplot(data_gridspec[1, 1])
        magnetic_field_map_swath_axis = \
            self._figure.add_subplot(data_gridspec[1, 3])
        magnetic_field_map_globe_axis = \
            self._figure.add_subplot(data_gridspec[1, 4])

        surface_map_globe_axis.set_aspect('equal')
        magnetic_field_map_globe_axis.set_aspect('equal')

        return {'surface_swath': surface_map_swath_axis,
                'surface_globe': surface_map_globe_axis,
                'magnetic_field_swath': magnetic_field_map_swath_axis,
                'magnetic_field_globe': magnetic_field_map_globe_axis}

    def _make_angle_axes(self) -> dict:
        angle_gridspec = self._gridspec['angle']
        solar_zenith_angle_axis = \
            self._figure.add_subplot(angle_gridspec[0, 0])
        emission_angle_axis = self._figure.add_subplot(angle_gridspec[0, 1])
        phase_angle_axis = self._figure.add_subplot(angle_gridspec[0, 2])
        local_time_axis = self._figure.add_subplot(angle_gridspec[0, 3])

        return {'solar_zenith_angle': solar_zenith_angle_axis,
                'emission_angle': emission_angle_axis,
                'phase_angle': phase_angle_axis,
                'local_time': local_time_axis}

    def _add_colorbars(self) -> None:
        self._add_no_data_colorbar()
        self._add_aurora_data_colorbar()
        self._add_magnetic_field_map_colorbar()
        self._add_solar_zenith_angle_colorbar()
        self._add_emission_angle_colorbar()
        self._add_phase_angle_colorbar()
        self._add_local_time_colorbar()

    def _add_no_data_colorbar(self) -> None:
        data_gridspec = self._gridspec['data']
        cmap = plt.get_cmap('viridis')
        cax = self._figure.add_subplot(data_gridspec[0, 2])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=4)
        self._place_vertical_colorbar(
            sm,
            cax=cax,
            label='NO Nightglow Brightness [kR]',
            major_tick_spacing=1,
            minor_tick_spacing=0.25)

        key = 'no'
        self._color_maps[key] = cmap
        self._norms[key] = norm

    def _add_aurora_data_colorbar(self) -> None:
        data_gridspec = self._gridspec['data']
        cmap = plt.get_cmap('magma')
        cax = self._figure.add_subplot(data_gridspec[0, 5])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=1)
        self._place_vertical_colorbar(
            sm,
            cax=cax,
            label='Aurora Brightness [kR]',
            major_tick_spacing=0.5,
            minor_tick_spacing=0.125)

        key = 'aurora'
        self._color_maps[key] = cmap
        self._norms[key] = norm

    def _add_magnetic_field_map_colorbar(self) -> None:
        data_gridspec = self._gridspec['data']
        cmap = plt.get_cmap('Blues_r')
        cax = self._figure.add_subplot(data_gridspec[1, 5])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=1)
        self._place_vertical_colorbar(
            sm,
            cax=cax,
            label='Probability of Open Magnetic Field Line',
            major_tick_spacing=0.2,
            minor_tick_spacing=0.05)

        key = 'magnetic_field'
        self._color_maps[key] = cmap
        self._norms[key] = norm

    def _add_solar_zenith_angle_colorbar(self) -> None:
        angle_gridspec = self._gridspec['angle']
        cmap = plt.get_cmap('cividis_r')
        cax = self._figure.add_subplot(angle_gridspec[1, 0])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=180)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Solar Zenith Angle [degrees]',
            major_tick_spacing=30,
            minor_tick_spacing=5)

        key = 'angle'
        self._color_maps[key] = cmap
        self._norms[key] = norm

    def _add_emission_angle_colorbar(self) -> None:
        angle_gridspec = self._gridspec['angle']
        cmap = plt.get_cmap('cividis_r')
        cax = self._figure.add_subplot(angle_gridspec[1, 1])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=180)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Emission Angle [degrees]',
            major_tick_spacing=15,
            minor_tick_spacing=5)
        cax.set_xlim(0, 90)

    def _add_phase_angle_colorbar(self) -> None:
        angle_gridspec = self._gridspec['angle']
        cmap = plt.get_cmap('cividis_r')
        cax = self._figure.add_subplot(angle_gridspec[1, 2])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=180)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Phase Angle [degrees]',
            major_tick_spacing=30,
            minor_tick_spacing=5)

    def _add_local_time_colorbar(self) -> None:
        angle_gridspec = self._gridspec['angle']
        cmap = plt.get_cmap('twilight_shifted')
        cax = self._figure.add_subplot(angle_gridspec[1, 3])
        sm, norm = self._make_scalar_mappable(cmap, vmin=6, vmax=18)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Dayside Local Time [hours]',
            major_tick_spacing=3,
            minor_tick_spacing=1)

        key = 'local_time'
        self._color_maps[key] = cmap
        self._norms[key] = norm

    @staticmethod
    def _make_scalar_mappable(cmap, vmin, vmax):
        norm = colors.Normalize(vmin=vmin, vmax=vmax)
        scalar_mappable = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        scalar_mappable.set_array([])
        return scalar_mappable, norm

    @staticmethod
    def _place_vertical_colorbar(scalar_mappable, cax, label,
                                 major_tick_spacing=None,
                                 minor_tick_spacing=None):
        cbar = plt.colorbar(scalar_mappable, cax=cax, label=label)
        cbar.ax.set_rasterized(True)
        if major_tick_spacing is not None:
            cbar.ax.yaxis.set_major_locator(
                ticker.MultipleLocator(major_tick_spacing))
        if minor_tick_spacing is not None:
            cbar.ax.yaxis.set_minor_locator(
                ticker.MultipleLocator(minor_tick_spacing))
        return cbar

    @staticmethod
    def _place_horizontal_colorbar(scalar_mappable, cax, label,
                                   major_tick_spacing=None,
                                   minor_tick_spacing=None):
        cbar = plt.colorbar(scalar_mappable, cax=cax, label=label,
                            orientation='horizontal')
        cbar.ax.set_rasterized(True)
        if major_tick_spacing is not None:
            cbar.ax.xaxis.set_major_locator(
                ticker.MultipleLocator(major_tick_spacing))
        if minor_tick_spacing is not None:
            cbar.ax.xaxis.set_minor_locator(
                ticker.MultipleLocator(minor_tick_spacing))
        return cbar

    @property
    def figure(self):
        return self._figure

    @property
    def left_text(self):
        return self._text_axes['left']

    @property
    def center_text(self):
        return self._text_axes['center']

    @property
    def right_text(self):
        return self._text_axes['right']

    @property
    def no_data_swath(self) -> plt.Axes:
        return self._data_axes['no_swath']

    @property
    def no_data_globe(self) -> plt.Axes:
        return self._data_axes['no_globe']

    @property
    def aurora_data_swath(self) -> plt.Axes:
        return self._data_axes['aurora_swath']

    @property
    def aurora_data_globe(self) -> plt.Axes:
        return self._data_axes['aurora_globe']

    @property
    def surface_map_swath(self) -> plt.Axes:
        return self._map_axes['surface_swath']

    @property
    def surface_map_globe(self) -> plt.Axes:
        return self._map_axes['surface_globe']

    @property
    def magnetic_field_map_swath(self) -> plt.Axes:
        return self._map_axes['magnetic_field_swath']

    @property
    def magnetic_field_map_globe(self) -> plt.Axes:
        return self._map_axes['magnetic_field_globe']

    @property
    def solar_zenith_angle_swath(self) -> plt.Axes:
        return self._angle_axes['solar_zenith_angle']

    @property
    def emission_angle_swath(self) -> plt.Axes:
        return self._angle_axes['emission_angle']

    @property
    def phase_angle_swath(self) -> plt.Axes:
        return self._angle_axes['phase_angle']

    @property
    def local_time_swath(self) -> plt.Axes:
        return self._angle_axes['local_time']

    @property
    def angle_colormap(self):
        return self._color_maps['angle']

    @property
    def angle_norm(self):
        return self._norms['angle']

    @property
    def local_time_colormap(self):
        return self._color_maps['local_time']

    @property
    def local_time_norm(self):
        return self._norms['local_time']

    @property
    def no_colormap(self):
        return self._color_maps['no']

    @property
    def no_norm(self):
        return self._norms['no']

    @property
    def aurora_colormap(self):
        return self._color_maps['aurora']

    @property
    def aurora_norm(self):
        return self._norms['aurora']

    @property
    def magnetic_field_colormap(self):
        return self._color_maps['magnetic_field']

    @property
    def magnetic_field_norm(self):
        return self._norms['magnetic_field']
