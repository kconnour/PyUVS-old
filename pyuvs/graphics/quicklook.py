
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox


class Quicklook:
    def __init__(self, n_swaths: int) -> None:
        self.__n_swaths = n_swaths

    def make_standard_ql(self):
        self.__draw_standard_ql()
        # Add banner
        # Add dayside
        # add nightside
        # Add geometry
        # add Local time
        # add sza
        # add ea
        # add pa

    def __draw_standard_ql(self, bg_color=(0, 0, 0, 1)):

        fig = plt.figure(figsize=(5, 10))

        ql_axis = self.__add_ax(fig, 0.05, 0.95, 5/8, 7/8, bg_color=bg_color)
        geo_axis = self.__add_ax(fig, 0.05, 0.95, 1/4 + 3/32, 5/8-1/32, bg_color=bg_color)
        ls_axis = self.__add_ax(fig, 0.05, 0.475, 3/16, 1/4+1/16, bg_color=bg_color)
        sza_axis = self.__add_ax(fig, 0.525, 0.95, 3/16, 1/4+1/16, bg_color=bg_color)
        ea_axis = self.__add_ax(fig, 0.05, 0.475, 1/32, 1/32+1/8, bg_color=bg_color)
        pa_axis = self.__add_ax(fig, 0.525, 0.95, 1/32, 1/32+1/8, bg_color=bg_color)

    def __add_ax(self, fig, hmin: float, hmax: float, vmin: float, vmax: float,
                 bg_color=(0, 0, 0, 1)) -> plt.axis:

        axis = fig.add_subplot(1, 1, 1)
        axis.set_position(Bbox([[hmin, vmin], [hmax, vmax]]))
        axis.set_facecolor(bg_color)
        self.__turn_off_ticks(axis)
        self.__set_axis_limits(axis)

        return axis

    @staticmethod
    def __turn_off_ticks(axis) -> None:
        axis.set_xticks([])
        axis.set_yticks([])

    def __set_axis_limits(self, axis):
        slit_width = 10.64
        axis.set_xlim(0, slit_width * self.__n_swaths)
        axis.set_ylim(60, 120)

    @staticmethod
    def savefig(location):
        plt.savefig(location, dpi=300)

    '''@staticmethod
    def __make_solid_text() -> None:
        # Make sure the typeface isn't outlined when saved as a .pdf
        plt.rc('pdf', fonttype=42)  # ???
        plt.rc('ps', fonttype=42)  # postscript

    def __set_font_stuff(self, text_color) -> None:
        """
        Parameters
        ----------
        text_color
            The rbg tuple to make the text

        """
        plt.rc('font', size=self.__font_size)
        plt.rc('axes', titlesize=self.__font_size)
        plt.rc('axes', labelsize=self.__font_size)
        plt.rc('axes', titlepad=3)  # Set a little space around the title
        plt.rc('figure', titlesize=self.__font_size)
        plt.rc('font', **{'family': 'STIXGeneral'})  # Set the typeface to stix
        plt.rc('mathtext', fontset='stix')  # Set all math font to stix
        plt.rc('text', usetex=False)
        plt.rc('text', color=text_color)

    def __set_border_thickness(self) -> None:
        plt.rc('lines', linewidth=0.8)
        plt.rc('axes', linewidth=0.4)
        plt.rcParams.update({'font.size': self.__font_size})

    def __set_quicklook_rc_params(self, text_color):
        self.__make_solid_text()
        self.__set_font_stuff(text_color)
        self.__set_border_thickness()

    def __quicklook_setup(self, n_swaths,
                        bg_color=(0, 0, 0, 1), text_color=(1, 1, 1, 1)):
        """ Setup the quicklook

        Parameters
        ----------
        orbit: int
            The orbit to make the map of
        n_swaths
        text: bool, optional
            Denote whether text should be added to the image. Default is True
        bg_color: tuple, optional
            Set the background color to be the given rgba value. Default is (0, 0, 0, 1), i.e. opaque black
        text_color: tuple, optional
            Set the text color to be the given rgba value. Default is (1, 1, 1, 1), i.e. opaque white

        Returns
        -------
        axis: matplotlib axis
            The plt axis
        """
        self.__set_quicklook_rc_params(text_color)

        # Make a figure
        fig = plt.figure()
        axis = fig.add_subplot(position=[0.05, 0.05, 0.9, 0.9])

        # Set the background to be the user specified color
        axis.set_facecolor(bg_color)

        # Turn off the ticks
        axis.set_xticks([])
        axis.set_yticks([])

        # Set the axis limits
        slit_width = 10.64
        axis.set_xlim(0, slit_width * n_swaths)
        axis.set_ylim(60, 120)  # Mirror angle can go from 60 to 120

        return axis



    # add dayside method
    # add nightside method
    # add miniplot (LT, SZA, EA, PA; position)'''


if __name__ == '__main__':
    ql = Quicklook(8)
    ql.make_standard_ql()
    ql.savefig('/home/kyle/qltest.png')
