
import csv
import numpy as np

datafile = "CHSHBellTest/CHSHBellTest_60seconds_S242_U0002.csv"

class BellTest():
    def __init__(self, filename):
        
        self.pol_a = np.zeros(4)
        self.pol_t = np.zeros(4)
        self.counts = np.zeros((4,4))

        self._set_polarization_angles_and_counts(filename)
        
    def _set_polarization_angles_and_counts(self, filename:str) -> None:
        """
        Extracts values for polarization angles of A and T and the corresponding photon counts
        from a .csv from the thorlabs BellTest experiment
        """

        # Use "cp1252" since .csv from Thorlabs isn't saved as utf-8
        with open(filename, "r", encoding="cp1252") as f:
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

    def calculate_expectation_value(self, alpha:float, beta:float) -> tuple[float, float]:
        """
        Calculate expectation value as per page II-46 of the Thorlabs Quantum Optics Kit manual
        """
        a_index = np.where(self.pol_a == beta)[0][0]
        t_index = np.where(self.pol_t == alpha)[0][0]

        # R_ij are coincidence rates measured in configuration ij, tl = topleft
        # Index the counts matrix for a certain color eg Red like in figure 215 from page II-46 of the Thorlabs Quantum Optics Kit manual
        R_tl = self.counts[t_index, a_index]
        R_tr = self.counts[t_index, a_index + 2]
        R_bl = self.counts[t_index + 2, a_index]
        R_br = self.counts[t_index + 2, a_index + 2]

        numerator = R_tl - R_tr - R_bl + R_br
        N = R_tl + R_tr + R_bl + R_br # total counts

        E = numerator / N

        sigma_E_squared = 4*(R_tl + R_br)*(R_tr + R_bl) / (N**3) #TODO: this expression is vibe-coded and should be verified

        return E, sigma_E_squared

    def calculate_s_value(self) -> tuple[float, float]:
        """
        Calculate S value as per page II-46 of the Thorlabs Quantum Optics Kit
        """
        E_0_225, sigma_E_0_225_squared = self.calculate_expectation_value(0, 22.5)
        E_0_675, sigma_E_0_675_squared = self.calculate_expectation_value(0, 67.5)
        E_45_225, sigma_E_45_225_squared = self.calculate_expectation_value(45, 22.5)
        E_45_675, sigma_E_45_675_squared = self.calculate_expectation_value(45, 67.5)

        # Minus sign is not a typo
        S = E_0_225 - E_0_675 + E_45_225 + E_45_675

        S_uncertainty = np.sqrt(sigma_E_0_225_squared + sigma_E_0_675_squared + sigma_E_45_225_squared + sigma_E_45_675_squared)

        return S, S_uncertainty



bt = BellTest(datafile)

print(bt.calculate_s_value())
