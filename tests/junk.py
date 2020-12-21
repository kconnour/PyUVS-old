import numpy as np
from scipy.optimize import curve_fit


class ExternalEquilibriumMoistureContentFile:
    def __init__(self, file_path):
        assert isinstance(file_path, str), 'file_path must be a string'
        self.file_path = file_path
        self.temperatures = np.linspace(20, 100, num=int((100 - 20) / 5 + 1))
        self.relative_humidities = np.linspace(5, 95, num=int((95 - 5) / 5 + 1)) / 100

    def read_array(self):
        with open(self.file_path) as f:
            n_columns = len(f.readline().split(','))
        return np.loadtxt(self.file_path, delimiter=',', skiprows=1, usecols=range(1, n_columns))


class FitGrid:
    def __init__(self, emc):
        assert isinstance(emc, ExternalEquilibriumMoistureContentFile), 'emc must be an external file'
        self.emc = emc
        self.table, self.flat_table, self.flat_temps, self.flat_humidities = self.__prepare_inputs()
        self.fit = self.__perform_curve_fit()
        self.fitted_table = self.__fit_table()

    def __prepare_inputs(self):
        emc_table = self.emc.read_array()
        flattened_table = emc_table.flatten()
        flat_temps = np.tile(self.emc.temperatures, emc_table.shape[0])
        flat_humidities = np.repeat(self.emc.relative_humidities, emc_table.shape[1])

        return emc_table, flattened_table, flat_temps, flat_humidities

    def __perform_curve_fit(self):
        return curve_fit(self.__poly_fit, (self.flat_humidities, self.flat_temps), self.flat_table)[0]

    @staticmethod
    def __poly_fit(humidity_temperature, c, x1, x2, x3, x4, x5, x6, x7, y1, y2, y3, y4, y5, y6, y7):
        # This is really ugly but essentially I'm assuming a separable solution where each polynomial is up to 6 orders
        rh, t = humidity_temperature
        return c + np.polyval([x1, x2, x3, x4, x5, x6, x7], t) * np.polyval([y1, y2, y3, y4, y5, y6, y7], rh)

    def __fit_table(self):
        temp_grid, humidity_grid = np.meshgrid(self.emc.temperatures, self.emc.relative_humidities)
        return self.__poly_fit((humidity_grid, temp_grid), self.fit[0], self.fit[1], self.fit[2], self.fit[3],
                               self.fit[4], self.fit[5], self.fit[6], self.fit[7], self.fit[8], self.fit[9],
                               self.fit[10], self.fit[11], self.fit[12], self.fit[13], self.fit[14])

    def check_fit(self):
        grid_difference = self.emc.read_array() - self.fitted_table
        self.print_differences(grid_difference)

    def print_differences(self, grid_delta):
        abs_grid_diff = np.abs(grid_delta)
        max_difference = np.amax(abs_grid_diff)
        mean_difference = np.median(abs_grid_diff)
        worst_ind = np.where(max_difference == abs_grid_diff)
        print('The median difference is {}'.format(mean_difference))
        print('The worst difference was {}'.format(max_difference))
        print('At T = {} and RH = {} the grid = {}; prediction = {}'.format(self.emc.temperatures[worst_ind[1]][0],
                                                                            self.emc.relative_humidities[worst_ind[0]][
                                                                                0], self.emc.read_array()[worst_ind],
                                                                            self.fitted_table[worst_ind]))


class ResultantEquations:
    # Explicitly hold the way to turn fit coefficients into usable equations
    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

    def corn_equation(self):
        temp_sum = -1.87750082e+03 + \
                   1.53700740e+01 * self.temperature + \
                   -2.53523936e-01 * self.temperature ** 2 + \
                   3.60483186e-03 * self.temperature ** 3 + \
                   -3.11975536e-05 * self.temperature ** 4 + \
                   1.36966606e-07 * self.temperature ** 5 + \
                   -2.20885811e-10 * self.temperature ** 6
        humidity_sum = -2.44018788e-03 + \
                       -2.43161484e-02 * self.humidity + \
                       3.27399896e-02 * self.humidity ** 2 + \
                       3.94051454e-03 * self.humidity ** 3 + \
                       -1.38560075e-01 * self.humidity ** 4 + \
                       2.06176932e-01 * self.humidity ** 5 + \
                       -9.71319334e-02 * self.humidity ** 6

        return np.rint((-1.81935242 + temp_sum * humidity_sum) * 10) / 10

    def soybean_equation(self):
        temp_sum = 6.22820389e+04 + \
                   -5.73719676e+02 * self.temperature + \
                   2.33601757e+01 * self.temperature ** 2 + \
                   -6.51241832e-01 * self.temperature ** 3 + \
                   9.81067967e-03 * self.temperature ** 4 + \
                   -7.47522953e-05 * self.temperature ** 5 + \
                   2.25729252e-07 * self.temperature ** 6
        humidity_sum = 2.95579491e-05 + \
                       2.00530990e-04 * self.humidity + \
                       1.36527554e-03 * self.humidity ** 2 + \
                       -6.53080946e-03 * self.humidity ** 3 + \
                       1.45535667e-02 * self.humidity ** 4 + \
                       -1.50162806e-02 * self.humidity ** 5 + \
                       5.98417454e-03 * self.humidity ** 6

        return np.rint((-1.04671733 + temp_sum * humidity_sum) * 10) / 10


def corn_equation(temperature, humidity):
    temp_sum = -1.87750082e+03 + \
               1.53700740e+01 * temperature + \
               -2.53523936e-01 * temperature ** 2 + \
               3.60483186e-03 * temperature ** 3 + \
               -3.11975536e-05 * temperature ** 4 + \
               1.36966606e-07 * temperature ** 5 + \
               -2.20885811e-10 * temperature ** 6
    humidity_sum = -2.44018788e-03 + \
                   -2.43161484e-02 * humidity + \
                   3.27399896e-02 * humidity ** 2 + \
                   3.94051454e-03 * humidity ** 3 + \
                   -1.38560075e-01 * humidity ** 4 + \
                   2.06176932e-01 * humidity ** 5 + \
                   -9.71319334e-02 * humidity ** 6

    return np.rint((-1.81935242 + temp_sum * humidity_sum) * 10) / 10


print(corn_equation(33, .75))
