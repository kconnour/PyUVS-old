from pathlib import Path
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpecFromSubplotSpec


class ApoapseMUVQuicklook:
    def __init__(self, figure_width: float = 14):
        self._figure = self._make_figure(figure_width)

        text_gridspec, data_gridspec, angle_gridspec = self._make_gridspecs()

        self.left_text_axis, self.center_text_axis, self.right_text_axis = \
            self._add_text_axes_to_figure(text_gridspec)
        self.no_swath_axis, self.no_globe_axis, self.aurora_swath_axis, \
            self.aurora_globe_axis = \
            self._add_data_axes_to_figure(data_gridspec)
        self.surface_map_swath_axis, self.surface_map_globe_axis, \
            self.magnetic_field_map_swath_axis, \
            self.magnetic_field_map_globe_axis = \
            self._add_map_axes_to_figure(data_gridspec)
        self.solar_zenith_angle_axis, self.emission_angle_axis, \
            self.phase_angle_axis, self.local_time_axis = \
            self._add_angle_axes_to_figure(angle_gridspec)

        self._add_no_data_colorbar(data_gridspec)
        self._add_aurora_data_colorbar(data_gridspec)
        self._add_magnetic_field_map_colorbar(data_gridspec)
        self._add_solar_zenith_angle_colorbar(angle_gridspec)
        self._add_emission_angle_colorbar(angle_gridspec)
        self._add_phase_angle_colorbar(angle_gridspec)
        self._add_local_time_colorbar(angle_gridspec)

        del text_gridspec, data_gridspec, angle_gridspec

    def _make_figure(self, figure_width: float) -> plt.Figure:
        self._set_rc_params()
        return plt.figure(figsize=(figure_width, figure_width * 9 / 16),
                          constrained_layout=True,
                          dpi=100)

    @staticmethod
    def _set_rc_params() -> None:
        rc = Path(__file__).parent.resolve() / 'apoapse_muv_quicklook.mplstyle'
        plt.style.use(rc)

    def _make_gridspecs(self) -> tuple[GridSpecFromSubplotSpec,
                                       GridSpecFromSubplotSpec,
                                       GridSpecFromSubplotSpec]:
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
        return text_gridspec, data_gridspec, angle_gridspec

    def _add_text_axes_to_figure(self, text_gridspec) -> tuple:
        left_text_axis = self._figure.add_subplot(text_gridspec[0])
        center_text_axis = self._figure.add_subplot(text_gridspec[1])
        right_text_axis = self._figure.add_subplot(text_gridspec[2])
        return left_text_axis, center_text_axis, right_text_axis

    def _add_data_axes_to_figure(self, data_gridspec) -> tuple:
        no_swath_axis = self._figure.add_subplot(data_gridspec[0, 0])
        no_globe_axis = self._figure.add_subplot(data_gridspec[0, 1])
        aurora_swath_axis = self._figure.add_subplot(data_gridspec[0, 3])
        aurora_globe_axis = self._figure.add_subplot(data_gridspec[0, 4])

        no_globe_axis.set_aspect('equal')
        aurora_globe_axis.set_aspect('equal')

        return no_swath_axis, no_globe_axis, aurora_swath_axis, \
            aurora_globe_axis

    def _add_map_axes_to_figure(self, data_gridspec):
        surface_map_swath_axis = self._figure.add_subplot(data_gridspec[1, 0])
        surface_map_globe_axis = self._figure.add_subplot(data_gridspec[1, 1])
        magnetic_field_map_swath_axis = \
            self._figure.add_subplot(data_gridspec[1, 3])
        magnetic_field_map_globe_axis = \
            self._figure.add_subplot(data_gridspec[1, 4])

        surface_map_globe_axis.set_aspect('equal')
        magnetic_field_map_globe_axis.set_aspect('equal')

        return surface_map_swath_axis, surface_map_globe_axis, \
            magnetic_field_map_swath_axis, magnetic_field_map_globe_axis

    def _add_angle_axes_to_figure(self, angle_gridspec):
        solar_zenith_angle_axis = \
            self._figure.add_subplot(angle_gridspec[0, 0])
        emission_angle_axis = self._figure.add_subplot(angle_gridspec[0, 1])
        phase_angle_axis = self._figure.add_subplot(angle_gridspec[0, 2])
        local_time_axis = self._figure.add_subplot(angle_gridspec[0, 3])

        return solar_zenith_angle_axis, emission_angle_axis, \
            phase_angle_axis, local_time_axis

    def _add_no_data_colorbar(self, data_gridspec) -> None:
        cmap = plt.get_cmap('viridis')
        cax = self._figure.add_subplot(data_gridspec[0, 2])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=4)
        self._place_vertical_colorbar(
            sm,
            cax=cax,
            label='NO Nightglow Brightness [kR]',
            major_tick_spacing=1,
            minor_tick_spacing=0.25)

    def _add_aurora_data_colorbar(self, data_gridspec) -> None:
        cmap = plt.get_cmap('magma')
        cax = self._figure.add_subplot(data_gridspec[0, 5])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=2)
        self._place_vertical_colorbar(
            sm,
            cax=cax,
            label='Aurora Brightness [kR]',
            major_tick_spacing=0.5,
            minor_tick_spacing=0.125)

    def _add_magnetic_field_map_colorbar(self, data_gridspec) -> None:
        cmap = plt.get_cmap('Blues_r')
        cax = self._figure.add_subplot(data_gridspec[1, 5])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=1)
        self._place_vertical_colorbar(
            sm,
            cax=cax,
            label='Probability of Open Magnetic Field Line',
            major_tick_spacing=0.2,
            minor_tick_spacing=0.05)

    def _add_solar_zenith_angle_colorbar(self, angle_gridspec) -> None:
        cmap = plt.get_cmap('cividis_r')
        cax = self._figure.add_subplot(angle_gridspec[1, 0])
        sm, norm = self._make_scalar_mappable(cmap, vmin=0, vmax=180)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Solar Zenith Angle [degrees]',
            major_tick_spacing=30,
            minor_tick_spacing=5)

    def _add_emission_angle_colorbar(self, angle_gridspec) -> None:
        cmap = plt.get_cmap('cividis_r')
        cax = self._figure.add_subplot(angle_gridspec[1, 1])
        sm, _ = self._make_scalar_mappable(cmap, vmin=0, vmax=180)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Emission Angle [degrees]',
            major_tick_spacing=15,
            minor_tick_spacing=5)
        cax.set_xlim(0, 90)

    def _add_phase_angle_colorbar(self, angle_gridspec) -> None:
        cmap = plt.get_cmap('cividis_r')
        cax = self._figure.add_subplot(angle_gridspec[1, 2])
        sm, _ = self._make_scalar_mappable(cmap, vmin=0, vmax=180)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Phase Angle [degrees]',
            major_tick_spacing=30,
            minor_tick_spacing=5)

    def _add_local_time_colorbar(self, angle_gridspec) -> None:
        cmap = plt.get_cmap('twilight_shifted')
        cax = self._figure.add_subplot(angle_gridspec[1, 3])
        sm, norm = self._make_scalar_mappable(cmap, vmin=6, vmax=18)
        self._place_horizontal_colorbar(
            sm,
            cax=cax,
            label='Dayside Local Time [hours]',
            major_tick_spacing=3,
            minor_tick_spacing=1)

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
