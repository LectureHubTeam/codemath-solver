import pandas as pd

from base_solver.shared_utils import normalize_points


def get_filtered_problems(
    csv_file,
    solved=None,
    difficulty=None,  # LQDOJ có thể dùng difficulty thay vì category
    sort_by="ac-rate",
    ascending=True,
    limit: int = 0,
):
    df = pd.read_csv(csv_file, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    # Xử lý ac-rate nếu có
    if "ac-rate" in df.columns:
        df["ac-rate"] = df["ac-rate"].str.strip()
        df["ac-rate"] = df["ac-rate"].str.replace(",", ".")
        df["ac-rate"] = df["ac-rate"].str.rstrip("%").astype(float)

    # Xử lý difficulty (LQDOJ specific)
    if "difficulty" in df.columns:
        df["difficulty"] = df["difficulty"].str.strip()

    # Xử lý category nếu có (backward compatibility)
    if "category" in df.columns:
        df["category"] = df["category"].str.strip()

    df["problem-code"] = df["problem-code"].str.strip()

    if solved is not None:
        df = df[df["solved"] == solved]

    # Filter by difficulty (LQDOJ) hoặc category (CodeMath)
    if difficulty and "difficulty" in df.columns:
        df = df[df["difficulty"] == difficulty]
    elif difficulty and "category" in df.columns:
        # Fallback to category if difficulty not available
        df = df[df["category"] == difficulty]

    if sort_by in ["ac-rate", "users"] and sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)
    elif sort_by == "points" and "points" in df.columns:
        # Normalize points for sorting
        df["points_normalized"] = df["points"].apply(normalize_points)
        df = df.sort_values(by="points_normalized", ascending=ascending)
        # Remove temporary column
        df = df.drop(columns=["points_normalized"])

    problems = df["problem-code"].tolist()
    if limit > 0:
        return problems[:limit], df[:limit]
    return problems, df


if __name__ == "__main__":
    filtered_problems, df = get_filtered_problems(
        "lqdoj_problems_data.csv",
        solved=-1,
        difficulty="Hard",  # LQDOJ có thể dùng Easy, Medium, Hard
        sort_by="ac-rate",
        ascending=False,
        limit=10,
    )
    print(filtered_problems)
    print(df)
