"""The :code:`templates` module provides templates for creating graphics."""

from pathlib import Path
import matplotlib.pyplot as plt


class Plain:
    pass


class ExtendedApoapseQuicklook:
    pass


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
        plt.style.use(Path(__file__).parent.joinpath('rcparams.mplstyle'))
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
    ql = StandardApoapseQuicklook()
    plt.savefig('/home/kyle/test.pdf')
