def compare_columns(df1, df2, name1="df1", name2="df2"):
    c1, c2 = set(df1.columns), set(df2.columns)

    only_in_1 = sorted(c1 - c2)
    only_in_2 = sorted(c2 - c1)
    common    = [c for c in df1.columns if c in df2.columns]

    print(f"Columns only in {name1} ({len(only_in_1)}):", only_in_1)
    print(f"Columns only in {name2} ({len(only_in_2)}):", only_in_2)
    print(f"Common columns ({len(common)}). Example:", common[:10])