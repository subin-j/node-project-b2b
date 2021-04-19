import pandas as pd


<<<<<<< HEAD
corporation_df = pd.read_csv('기업정보.csv', dtype=str)

columns = corporation_df.columns.tolist()
print(columns)

for row in corporation_df.itertuples():

    print(row.cocode)
=======
df = pd.read_csv("기업정보.csv", dtype=str)
>>>>>>> main
