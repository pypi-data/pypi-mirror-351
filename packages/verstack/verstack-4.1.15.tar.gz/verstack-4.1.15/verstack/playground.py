import pandas as pd
df = pd.read_csv('/Users/danil/Downloads/clients.csv', on_bad_lines='skip', sep=';')

dp = DateParser(verbose=False)
data = dp.fit_transform(df)

from verstack.tools import Printer

printer = Printer(verbose=True)



print_output = pd.DataFrame(dp._created_datetime_cols)
printer.print(print_output.to_markdown(), order = 0 )


