import csv
import numpy as np
import pandas as pd

# read expected allocation file as dataframe
allo = pd.read_csv(
    '/Users/danielroyo2227/kodama/kodama222/dojima/tokenomics/data/expected_allocation.csv'
)

# group tokens and host in tuple
gb = allo.groupby('Token')
tokens = tuple(gb.get_group(x) for x in gb.groups)

# read template file as dataframe and read names of columns
template = pd.read_csv(
    '/Users/danielroyo2227/kodama/kodama222/jarvis/allos/template.csv'
)
l = list(template.DATA)
l.insert(0, 'DATA')
columns = l

# fill csv file for each token
for t in tokens:

    token_name = (t.Token.iloc[0]).lower()   # get token name as string

    # create allocation dataframe for token
    df1 = pd.DataFrame(
        t.drop(columns=['Token', 'Holder']).values, columns=columns[11:]
    )

    df2 = pd.DataFrame(t[['Holder']].values).rename(columns={0: 'entity'})
    df3 = pd.DataFrame(np.nan, index=range(0, len(df1)), columns=columns[5:11])

    df_c = pd.concat([df2, df3], axis=1)

    df = pd.concat([df2, df1], axis=1)

    # transpose dataframe, reset index and create list of lists
    transposed = df.T.reset_index().values
    l_t = [a.tolist() for a in transposed]

    # create list of lists for csv file
    l1 = [['DATA', '', '', '', '', '', ''], template.iloc[0].values]
    l2 = [token_name] + [None] * 6
    l3 = ['DISTRIBUTION'] + [None] * len(df2)

    l1.append(l2)
    l1.append(l3)
    l1.extend(l_t)

    # write list of lists to csv file
    with open(
        f'/Users/danielroyo2227/kodama/kodama222/jarvis/allos/csv_files/{token_name}.csv',
        'w',
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(l1)
