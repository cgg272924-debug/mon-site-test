import pandas as pd

print("=== STEP A — CLASSEMENT GÉNÉRAL LIGUE 1 (ROBUSTE) ===")

df = pd.read_csv("data/processed/ol_matches_rated.csv")

def get_points(result):
    if result == "W":
        return 3
    if result == "D":
        return 1
    return 0

teams = []

for _, row in df.iterrows():

    ol_points = get_points(row["result"])

    # OL
    teams.append({
        "team": "Lyon",
        "points": ol_points
    })

    # Adversaire
    if ol_points == 3:
        opp_points = 0
    elif ol_points == 1:
        opp_points = 1
    else:
        opp_points = 3

    teams.append({
        "team": row["opponent"],
        "points": opp_points
    })

table = pd.DataFrame(teams)

standings = (
    table.groupby("team", as_index=False)
    .agg(
        points=("points", "sum"),
        matches=("points", "count")
    )
)

standings["points_per_match"] = (standings["points"] / standings["matches"]).round(2)

standings = standings.sort_values(
    ["points", "points_per_match"],
    ascending=False
).reset_index(drop=True)

standings["rank"] = standings.index + 1

standings.to_csv("data/processed/league1_standings.csv", index=False)

print("Fichier créé : data/processed/league1_standings.csv")
print("\nTOP 10 :")
print(standings.head(10))
