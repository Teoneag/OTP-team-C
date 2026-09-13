import csv
import numpy as np

datafile = "CHSHBellTest/CHSHBellTest_60seconds_S242_U0002.csv"
figure215_datafile = "CHSHBellTest/figure215_data.csv"

class BellTest():
    def __init__(self, filename):

        self.s_value = 0.0
        self.s_uncertainty = 0.0
        self.measurement_time = 0.0
        
        self.pol_a = np.zeros(4)
        self.pol_t = np.zeros(4)
        self.rates = np.zeros((4,4))
        self.counts = np.zeros((4,4))

        self._set_experiment_data(filename)
        self._set_s_value()

    def _set_experiment_data(self, filename:str) -> None:
        """
        Extracts values for polarization angles of A and T 
        and the corresponding photon rates (Hz) and counts
        from a .csv from the thorlabs BellTest experiment
        """
        # Use "cp1252" since .csv from Thorlabs isn't saved as utf-8
        with open(filename, "r", encoding="cp1252") as f:
            all_lines = f.readlines()

            meta_data = [line for line in all_lines if line.startswith("#")]
            measurement_data = [line for line in all_lines if not line.startswith("#")]

            # Extract measurement time from the metadata lines, e.g. "#60 seconds measurement time"
            for line in meta_data:
                if "seconds measurement time" in line:
                    self.measurement_time = float(line.split(" ")[0].strip("#"))
                    break
                
            reader = csv.reader(measurement_data, delimiter=";")

            header = next(reader) # get pol_T\pol_A line
            self.pol_a = np.array([float(x.replace(",", ".")) for x in header[1:]]) # Get the A polarization angles

            for i, row in enumerate(reader):
                self.pol_t[i] = (float(row[0].replace(",", "."))) # Get T polarization angles

                for j, x in enumerate(row[1:]):
                    rate = float(x.replace(",", "."))
                    self.rates[i,j] = rate                    
                    self.counts[i, j] = rate * self.measurement_time

    def _calculate_expectation_value(self, alpha:float, beta:float) -> tuple[float, float]:
        """
        Calculate expectation value as per page II-46 of the Thorlabs Quantum Optics Kit manual.
        Also calculates uncertainty using poisson assumption as outlined in section 12.5
        """
        a_index = np.where(self.pol_a == beta)[0][0]
        t_index = np.where(self.pol_t == alpha)[0][0]

        # R_ij are coincidence rates (Hz) measured in configuration ij, tl = topleft
        # Index the counts matrix for a certain color (eg Red) like in figure 215 from page II-46 of the Thorlabs Quantum Optics Kit manual
        R_tl = self.rates[t_index, a_index]
        R_tr = self.rates[t_index, a_index + 2]
        R_bl = self.rates[t_index + 2, a_index]
        R_br = self.rates[t_index + 2, a_index + 2]
        R_total = R_tl + R_tr + R_bl + R_br

        E = (R_tl - R_tr - R_bl + R_br) / R_total

        # Use counts for calculating uncertainty
        N_tl = self.counts[t_index, a_index]
        N_tr = self.counts[t_index, a_index + 2]
        N_bl = self.counts[t_index + 2, a_index]
        N_br = self.counts[t_index + 2, a_index + 2]
        N_total = N_tl + N_tr + N_bl + N_br

        sigma_E_squared = 4*(N_tl + N_br)*(N_tr + N_bl) / (N_total**3) # \sigma^2_E​=\sum_i​(\delta C_i / \delta E​)^2 * \sigma^2_{C_i}

        return E, sigma_E_squared

    def _set_s_value(self) -> None:
        """
        Calculate S value as per page II-46 of the Thorlabs Quantum Optics Kit.
        Also propagates the uncertainties from each expectation value.
        """
        E_0_225, sigma_E_0_225_squared = self._calculate_expectation_value(0, 22.5)
        E_0_675, sigma_E_0_675_squared = self._calculate_expectation_value(0, 67.5)
        E_45_225, sigma_E_45_225_squared = self._calculate_expectation_value(45, 22.5)
        E_45_675, sigma_E_45_675_squared = self._calculate_expectation_value(45, 67.5)

        # Minus sign is not a typo
        S = E_0_225 - E_0_675 + E_45_225 + E_45_675
        S_uncertainty = np.sqrt(sigma_E_0_225_squared + sigma_E_0_675_squared + sigma_E_45_225_squared + sigma_E_45_675_squared)

        self.s_value = S
        self.s_uncertainty = S_uncertainty

    def print_s_value(self, show_ndigits:int = 3) -> None:
        """
        Print S value and its uncertainty formatted as S +- s_uncertainty
        
        show_ndigits: number of decimal digits to display
        """
        available_ndigits = len(str(self.s_value).split(".")[1])
        ndigits = min(show_ndigits, available_ndigits)

        S = round(self.s_value, ndigits)
        s_uncertainty = round(self.s_uncertainty, ndigits)

        print(f"S = {S} +- {s_uncertainty}")


# bt = BellTest(datafile)
bt = BellTest(figure215_datafile)

bt.print_s_value(show_ndigits=5)
