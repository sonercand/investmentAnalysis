import pandas as pd

rawESG = pd.read_csv("./data/esg_ratings_raw.csv")
print(rawESG["rate"].unique())
dict_ = {"aaa": 7, "aa": 6, "a": 5, "bbb": 4, "bb": 3, "eb": 2, "b": 2, "ccc": 1}


def conv(row_, dict_):
    return dict_[row_]


rawESG["numericRate"] = rawESG.rate.apply((lambda x: conv(x, dict_)))

rawESG.to_csv("./data/esgScores.csv", index=False)
