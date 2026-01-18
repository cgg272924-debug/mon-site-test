import pandas as pd
from pathlib import Path
from math import sqrt

print("=== PROFILS TACTIQUES UNDERSTAT — SIMILARITE ENTRE EQUIPES ===")

DATA_DIR = Path("data/processed")
PROFILES_PATH = DATA_DIR / "league1_understat_team_profiles.csv"
OUTPUT_PATH = DATA_DIR / "league1_understat_team_similarity.csv"


def load_profiles() -> pd.DataFrame:
    if not PROFILES_PATH.exists():
        raise FileNotFoundError(str(PROFILES_PATH))
    df = pd.read_csv(PROFILES_PATH)
    if df.empty:
        raise RuntimeError("league1_understat_team_profiles.csv est vide")
    return df


def build_feature_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "xg_per_match",
        "xga_per_match",
        "shots_per90",
        "deep_per90",
        "deep_allowed_per90",
        "field_tilt_avg",
        "ppda_att_avg",
        "ppda_def_avg",
    ]
    df_num = df.copy()
    for c in cols:
        if c not in df_num.columns:
            df_num[c] = 0.0
        df_num[c] = pd.to_numeric(df_num[c], errors="coerce").fillna(0.0)
    grouped = df_num.groupby("team", as_index=False)[cols].mean()
    return grouped


def l2_distance(a, b) -> float:
    s = 0.0
    for x, y in zip(a, b):
        d = float(x) - float(y)
        s += d * d
    return sqrt(s)


def build_similarity(df_features: pd.DataFrame) -> pd.DataFrame:
    teams = df_features["team"].tolist()
    cols_feat = [c for c in df_features.columns if c != "team"]
    rows = []
    for i, team_a in enumerate(teams):
        vec_a = df_features.loc[df_features["team"] == team_a, cols_feat].iloc[0]
        distances = []
        for j, team_b in enumerate(teams):
            if team_a == team_b:
                continue
            vec_b = df_features.loc[df_features["team"] == team_b, cols_feat].iloc[0]
            dist = l2_distance(vec_a.values, vec_b.values)
            distances.append((team_b, dist))
        distances.sort(key=lambda x: x[1])
        top = distances[:5]
        for rank, (team_b, dist) in enumerate(top, start=1):
            rows.append(
                {
                    "team": team_a,
                    "similar_team": team_b,
                    "rank": rank,
                    "distance": dist,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    df_profiles = load_profiles()
    print("Profils chargés :", df_profiles.shape)
    df_features = build_feature_table(df_profiles)
    print("Table de features construite :", df_features.shape)
    df_sim = build_similarity(df_features)
    df_sim.to_csv(OUTPUT_PATH, index=False)
    print(f"Fichier de similarité créé : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

