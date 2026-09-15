import os
import csv
import numpy as np


def extract_value_from_line(line:str):
    """Helper function for extracting the numerical value from a line in a csv file with delimiter ';' and the decimal part separated by comma"""
    return float(line.split(";")[1].replace(",", ".").strip())

class GRA_exp():
    def __init__(self, filename:str):
        self.filename = filename
        
        self.g2_TAB = 0.0

        self.R_T = 0.0
        self.R_TA = 0.0
        self.R_TB = 0.0
        self.R_TAB = 0.0
        

        self._set_experiment_data(filename)

        self._set_correlation_function()

    def _set_experiment_data(self, filename:str):
        with open(filename, "r", encoding="cp1252") as f:
            all_lines = f.readlines()

            reader = csv.reader(all_lines, delimiter=";")


            rates = [line for line in all_lines if line.startswith("Rates (Hz):")]
            counts = [line for line in all_lines if line.startswith("Counts:")]
            correlations = [line for line in all_lines if line.startswith("g2(0)")]
            
            self.R_T = extract_value_from_line(rates[0])
            # self.R_A = extract_value(rates[1])
            # self.R_B = extract_value(rates[2])
            self.R_TA = extract_value_from_line(rates[3])
            self.R_TB = extract_value_from_line(rates[4])
            self.R_TAB = extract_value_from_line(rates[5])

            self.N_T = extract_value_from_line(counts[0])
            self.N_TA = extract_value_from_line(counts[3])
            self.N_TB = extract_value_from_line(counts[4])
            self.N_TAB = extract_value_from_line(counts[5])

            # self.capture_duration = all_lines[9]

    def _set_correlation_function(self, ):
        self.g2_TAB = self.R_TAB * self.R_T / (self.R_TA * self.R_TB)


def main():
    #Get all measurement csv files
    gra_csv_dir = "GRA/gra_csv_data/"
    files = os.listdir(gra_csv_dir)

    # Get the g2_TAB from every measurement
    results = np.zeros(len(files))
    for i, filename in enumerate(files):
        exp = GRA_exp(gra_csv_dir + filename)
        results[i] = exp.g2_TAB

    # Calculate expectation value, std dev, std error of the mean
    mean = results.mean()
    std = results.std(ddof=1) # degree of freedom default in numpy is 0, 1 is standard in calculations
    sem = std / np.sqrt(len(results))

    print(f"<g> = {mean:.5f} ± {sem:.5f}")


main()