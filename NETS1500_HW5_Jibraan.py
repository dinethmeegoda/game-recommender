import json
import math

import requests

def recommend_games_from_github(
    user_age=18,
    platform_filter=None,
    preferred_publishers=None,
    preferred_developers=None,
    preferred_genres=None,
    prefer_critic_over_user=True,
    top_n=20
):
    # Load the JSON from GitHub
    url = "https://raw.githubusercontent.com/dinethmeegoda/game-recommender/main/All_games_ever_made.json"
    response = requests.get(url)
    data = response.json()

    def age_rating_allowed(rating):
        if rating in ["Rated E", "Rated E +10"]: return user_age >= 10
        elif rating == "Rated T": return user_age >= 13
        elif rating == "Rated M": return user_age >= 17
        else: return True

    results = []
    for game, info in data.items():
        if not info.get("title") or not info.get("platforms"):
            continue

        if platform_filter and platform_filter not in info["platforms"]:
            continue
        if not age_rating_allowed(info.get("esrb_rating", "")):
            continue

        score = 0

        # Genre match
        game_genres = info.get("genres", [])
        if preferred_genres:
            genre_overlap = len(set(preferred_genres).intersection(set(game_genres)))
            score += 10 * genre_overlap

        # Developer/Publisher preference
        dev = info.get("developer", "").lower() if info.get("developer") else ""
        pub = info.get("publisher", "").lower() if info.get("publisher") else ""
        if preferred_developers and dev in [d.lower() for d in preferred_developers]:
            score += 15
        if preferred_publishers and pub in [p.lower() for p in preferred_publishers]:
            score += 10

        # Critic/User score weighting
        try:
            critic_score = float(info["critic_score"]) if info.get("critic_score") and info["critic_score"] != "tbd" else 0
            user_score = float(info["user_score"]) if info.get("user_score") and info["user_score"] != "tbd" else 0
        except:
            critic_score, user_score = 0, 0

        score += (0.7 * critic_score + 0.3 * user_score) if prefer_critic_over_user else (0.3 * critic_score + 0.7 * user_score)

        # Deprioritize childish games for older users
        if info.get("esrb_rating") == "Rated E" and user_age >= 20:
            score -= 5

        results.append({
            "title": info["title"],
            "score": score,
            "platforms": info["platforms"],
            "developer": dev,
            "publisher": pub,
            "genres": game_genres,
            "critic_score": critic_score,
            "user_score": user_score
        })

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]

if __name__ == "__main__":
    recommendations = recommend_games_from_github(
        user_age=16,
        platform_filter="Nintendo Switch",
        preferred_publishers=["Nintendo"],
        preferred_developers=["Nintendo"],
        preferred_genres=["Open-World Action", "3D Platformer"],
        prefer_critic_over_user=False
    )

    for game in recommendations:
        print(f"{game['title']} — Score: {round(game['score'], 2)}")
