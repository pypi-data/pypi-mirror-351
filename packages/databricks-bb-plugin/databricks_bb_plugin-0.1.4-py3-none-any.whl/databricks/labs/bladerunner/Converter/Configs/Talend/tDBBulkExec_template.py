df = %SRC_NODE_NAME%
target_table = "%TABLE%"
custom_query = "%CUSTOM_QUERY%"
columns_str = "%TARGET_COLUMNS%"

if(custom_query or custom_query != ''):
    spark.sql(f"""{custom_query}""")

if(columns_str or columns_str != ""):
    columns = columns_str.split(',')
    df.select([c for c in df.columns if c in columns])

df.write.saveAsTable(target_table, mode = 'append')