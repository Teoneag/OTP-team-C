
import csv
import numpy as np

datafile = "C:/Users/QuantumRules/Documents/OTP-team-C/CHSHBellTest_60seconds_S242_U0002.csv"

class BellTest():
    def __init__(self, filename):
        
        self.pol_a = np.zeros(4)
        self.pol_t = np.zeros(4)
        self.counts = np.zeros((4,4))

        self._get_polarization_angles_and_counts(filename)
        

    def _get_polarization_angles_and_counts(self, filename:str):
        with open(filename, "r") as f:
            # Ignore metadata lines
            lines = (line for line in f if not line.startswith("#"))
            reader = csv.reader(lines, delimiter=";")

            # header is pol_T\pol_A line
            header = next(reader)

            # Get the A polarization angles
            self.pol_a = np.array([float(x.replace(",", ".")) for x in header[1:]])

            for i, row in enumerate(reader):
                
                self.pol_t[i] = (float(row[0].replace(",", "."))) # Get T polarization angles

                for j, x in enumerate(row[1:]):
                    self.counts[i,j] = float(x.replace(",", "."))

    def calculate_expectation_value(self, alpha:float, beta:float) -> float:

        a_index = np.where(self.pol_a == beta)[0][0]
        t_index = np.where(self.pol_t == alpha)[0][0]

        R_tl = self.counts[t_index, a_index]
        R_tr = self.counts[t_index, a_index + 2]
        R_bl = self.counts[t_index + 2, a_index]
        R_br = self.counts[t_index + 2, a_index + 2]

        numerator = R_tl - R_tr - R_bl + R_br
        denominator = R_tl + R_tr + R_bl + R_br

        return numerator / denominator




    def calculate_s_value(self) -> tuple[float, float]:
        E_0_225 = self.calculate_expectation_value(0, 22.5)
        E_0_675 = self.calculate_expectation_value(0, 67.5)
        E_45_225 = self.calculate_expectation_value(45, 22.5)
        E_45_675 = self.calculate_expectation_value(45, 67.5)

        return E_0_225 - E_0_675 + E_45_225 + E_45_675



bt = BellTest(datafile)

print(bt.calculate_s_value())
