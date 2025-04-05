import pandas as pd


def get_filtered_problems(
    csv_file,
    solved=None,
    category=None,
    sort_by="ac-rate",
    ascending=True,
    limit: int = 0,
):
    df = pd.read_csv(csv_file, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    df["ac-rate"] = df["ac-rate"].str.strip()
    df["ac-rate"] = df["ac-rate"].str.replace(",", ".")
    df["ac-rate"] = df["ac-rate"].str.rstrip("%").astype(float)

    df["category"] = df["category"].str.strip()
    df["problem-code"] = df["problem-code"].str.strip()

    if solved is not None:
        df = df[df["solved"] == solved]
    if category:
        df = df[df["category"] == category]

    if sort_by in ["ac-rate", "users"]:
        df = df.sort_values(by=sort_by, ascending=ascending)

    print(df[["problem-code", "ac-rate"]])

    problems = df["problem-code"].tolist()
    if limit > 0:
        return problems[:limit], df[:limit]
    return problems, df


if __name__ == "__main__":
    filtered_problems, df = get_filtered_problems(
        "problems_data.csv",
        solved=-1,
        category="Nâng cao",
        sort_by="ac-rate",
        ascending=False,
        limit=10,
    )
    print(filtered_problems)
    print(df)
