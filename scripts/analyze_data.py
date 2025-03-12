import pandas as pd

def analyze_data(filename="spectrum_data.csv"):
    data = pd.read_csv(filename)
    print(data.describe())