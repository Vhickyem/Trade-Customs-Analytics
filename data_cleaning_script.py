# import libraries
import pandas as pd
import numpy as np

# open data
def wrangle(filepath):
    with open(filepath, "r") as file:
        df = pd.read_csv(file)
        
    # display first few rows of the dataframe
    print(df.head())
    # display the shape of the dataframe
    print(df.shape)
    # display the data types of each column
    print(df.dtypes)

    # Data wrangling
    # copy dataframe
    data = df.copy().drop(columns=["Unnamed: 0"])
    # Fill receipt number with 'Unknown'
    data["Receipt Number"] = data["Receipt Number"].fillna("Unknown")
    
    # Flag where Country of Supply matches Origin
    data["self_supply"] = data["Country  of Origin"] == data["Country  of Supply"]

    # Compute rate of self supply by origin
    self_supply_stats = (data.groupby("Country  of Origin")["self_supply"]
                        .mean()
                        .reset_index(name="Self Supply Rate"))
    # Convert to percentage
    self_supply_stats["Self Supply Rate"] = round(self_supply_stats["Self Supply Rate"] * 100, 2)
    
    # create a sort of lookup table for the country and self supply rate
    rate_dict = dict(
        zip(self_supply_stats["Country  of Origin"], self_supply_stats["Self Supply Rate"])
    )

    # create the imputation function, putting each row in consideration
    def impute_supply(row):
        origin = row["Country  of Origin"]
        supply = row["Country  of Supply"]
        
        # If the supply is present, keep it
        if pd.notna(supply):
            return supply
        # If supply is missing, check rule
        if rate_dict.get(origin, 0) >= 70:
            return origin # If rate >= 70
        else:
            return "Unknown"
        

    # Apply the function
    data["Country  of Supply"] = data.apply(impute_supply, axis=1)
    data.drop(columns="self_supply", inplace=True)
    
    # For Container Nbr and Container Size, if Nbr of Containers is 0,
    # It means, no container was used and we'll fill with Not Apllicable (N/A)
    #if Nbr of Containers >= 1, then we'll fill with unknown
    data["Container Nbr"] = np.where(
        data["Nbr Of Containers"] == '0', "N/A",
        data["Container Nbr"].fillna('Unknown')
    )

    data["Container Size"] = np.where(
        data["Nbr Of Containers"] == '0', "N/A",
        data["Container Size"].fillna('Unknown')
    )
    
    # Change an Outlier to 1
    data.loc[data["Nbr Of Containers"]=='3248477', 'Nbr Of Containers'] = '1'
    # Change W to 1
    data.loc[data["Nbr Of Containers"]=='W', 'Nbr Of Containers'] = '1'
    
    # change the years
    # create a mapping dictionary
    year_map = {
        1866: 2021,
        1867: 2022,
        1868: 2023,
        1869: 2024
    }

    # replace the years
    data["Receipt Date"] = data["Receipt Date"].apply(
        lambda x:
            x.replace(year=year_map[x.year]) if pd.notna(x) and x.year in year_map else x
    )
    
    # change data type of Importer
    data["Importer"] = data["Importer"].astype(str)
    # Change for HS Code
    data["HS Code"] = data["Importer"].astype(str)
    # Change Mass (KG) to integers
    data["Mass(KG)"] = data["Mass(KG)"].str.replace(",", "").astype(int)
    # Change Nbr Of Containers to integers
    data["Nbr Of Containers"] = data["Nbr Of Containers"].astype(int)