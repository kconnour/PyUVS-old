"""The :code:`colormaps` module provides colormaps commonly used in IUVS
graphics."""

import copy
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np


class Colormap:
    def __init__(self, cmap_name: str, vmin: float, vmax: float):
        self._cmap_name = cmap_name
        self._vmin = vmin
        self._vmax = vmax
        self._cmap = self._get_cmap()
        self._norm = self._set_norm()

    def _get_cmap(self):
        return plt.get_cmap(self._cmap_name)

    def _set_norm(self):
        return colors.Normalize(vmin=self._vmin, vmax=self._vmax)

    @property
    def cmap_name(self) -> str:
        return self._cmap_name

    @property
    def vmin(self) -> float:
        return self._vmin

    @property
    def vmax(self) -> float:
        return self._vmax

    @property
    def cmap(self) -> colors.LinearSegmentedColormap:
        return self._cmap

    @property
    def norm(self) -> colors.Normalize:
        return self._norm


class MagneticField(Colormap):
    def __init__(self):
        super().__init__('Blues_r', 0, 1)


class LocalTime(Colormap):
    def __init__(self):
        super().__init__('twilight_shifted', 6, 18)


class SolarZenithAngle(Colormap):
    def __init__(self):
        super().__init__('cividis_r', 0, 180)


class EmissionAngle(Colormap):
    def __init__(self):
        cividis_half = self._create_half_cmap()
        super().__init__(cividis_half, 0, 90)

    def _create_half_cmap(self):
        cividis_r = copy.copy(plt.get_cmap('cividis_r'))
        return colors.LinearSegmentedColormap.from_list(
            'cividis_half', cividis_r (np.linspace(0, 0.5, 256)))


class PhaseAngle(Colormap):
    def __init__(self):
        super().__init__('cividis_r', 0, 180)


if __name__ == '__main__':
    b = EmissionAngle()
    print(b.cmap_name)
    print(b.norm)
