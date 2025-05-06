import json
import math
from rapidfuzz import fuzz

import requests


def recommend_games_from_metacritic(
        user_age=16,
        platform_filter=None,
        preferred_publishers=None,
        preferred_developers=None,
        preferred_genres=None,
        prefer_critic_over_user=True,
        top_n=20,
        liked_games=None  # <-- new param
):
    # Load the JSON from GitHub
    url = ("https://raw.githubusercontent.com/dinethmeegoda/"
           "game-recommender/main/All_games_ever_made.json")
    response = requests.get(url)
    data = response.json()

    def age_rating_allowed(rating):
        if rating in ["Rated E", "Rated E +10"]:
            return user_age >= 10
        elif rating == "Rated T":
            return user_age >= 13
        elif rating == "Rated M":
            return user_age >= 17
        else:
            return True

    results = []
    for game, info in data.items():
        if not info.get("title") or not info.get("platforms"):
            continue

        if platform_filter:
            if isinstance(platform_filter, str):
                platform_filter = [platform_filter]
            if not any(
                    p in info.get("platforms", []) for p in platform_filter):
                continue

        if not age_rating_allowed(info.get("esrb_rating", "")):
            continue

        if liked_games is not None and info.get("title") in liked_games:
            continue

        score = 0

        # Genre match
        game_genres = info.get("genres", [])
        if preferred_genres:
            genre_overlap = len(set(preferred_genres).intersection(
                set(game_genres)))
            score += 10 * genre_overlap

        # Developer/Publisher preference using fuzzy matching
        dev = info.get("developer", "").lower() if info.get("developer") \
            else ""
        pub = info.get("publisher", "").lower() if info.get("publisher") \
            else ""
        if preferred_developers:
            for d in preferred_developers:
                if fuzz.token_set_ratio(d.lower(), dev) > 80:
                    score += 15
                    break

            # Fuzzy match publisher
        if preferred_publishers:
            for p in preferred_publishers:
                if fuzz.token_set_ratio(p.lower(), pub) > 80:
                    score += 10
                    break

        # Critic/User score weighting
        try:
            critic_score = float(info["critic_score"]) if (
                    info.get("critic_score") and info["critic_score"]
                    != "tbd") else 0
            user_score = float(info["user_score"]) if (
                    info.get("user_score") and info["user_score"] != "tbd") \
                else 0
        except:
            critic_score, user_score = 0, 0

        score += (0.7 * critic_score + 0.3 * user_score) if (
            prefer_critic_over_user) else (0.3 * critic_score + 0.7 *
                                           user_score)

        # Deprioritize childish games for older users
        if info.get("esrb_rating") == "Rated E" and user_age >= 20:
            score -= 5

        if liked_games:
            for liked_game in liked_games:
                liked_info = data.get(liked_game)
                if not liked_info:
                    continue
                # Similar genre
                liked_genres = set(liked_info.get("genres", []))
                current_genres = set(info.get("genres", []))
                genre_overlap = liked_genres.intersection(current_genres)
                if genre_overlap:
                    score += 10 * len(genre_overlap)

                # Same developer or publisher
                if liked_info.get("developer") and info.get("developer") and \
                        liked_info["developer"].lower() == info[
                    "developer"].lower():
                    score += 15
                if liked_info.get("publisher") and info.get("publisher") and \
                        liked_info["publisher"].lower() == info[
                    "publisher"].lower():
                    score += 10

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
    # Example Usage of Method
    recommendations = recommend_games_from_metacritic(
        user_age=16,
        platform_filter="PC",
        preferred_publishers=["EA"],
        preferred_developers=["Respawn Entertainment"],
        preferred_genres=["Open-World Action"],
        prefer_critic_over_user=False,
        liked_games=["Apex Legends"]
    )

    for game in recommendations:
        print(f"{game['title']} — Score: {round(game['score'], 2)}")
