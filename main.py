import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit,
    QTextEdit, QCheckBox, QGroupBox, QHBoxLayout
)
from RecommenderAlgorithm import recommend_games_from_metacritic

# Dineth Meegoda NETS 1500 HW5

class GameRecommenderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Recommender")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # Age input
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter your age")
        self.layout.addWidget(QLabel("Age:"))
        self.layout.addWidget(self.age_input)

        # Platform checkboxes
        self.platform_checkboxes = {
            "PC": QCheckBox("PC"),
            "Nintendo Switch": QCheckBox("Nintendo Switch"),
            "PlayStation 5": QCheckBox("PlayStation 5"),
            "Xbox One": QCheckBox("Xbox One"),
            "Xbox Series X": QCheckBox("Xbox Series X"),
            "PlayStation 4": QCheckBox("PlayStation 4"),
            "Xbox 360": QCheckBox("Xbox 360"),
            "PlayStation 3": QCheckBox("PlayStation 3"),
            "Wii": QCheckBox("Nintendo Wii"),
            "DS": QCheckBox("Nintendo DS"),
            "3DS": QCheckBox("Nintendo 3DS"),
            "Wii U": QCheckBox("Nintendo Wii U"),
            "iOS (iPhone/iPad)": QCheckBox("iOS"),
        }

        platform_box = QGroupBox("Select Platforms:")
        platform_layout = QHBoxLayout()
        for cb in self.platform_checkboxes.values():
            platform_layout.addWidget(cb)
        platform_box.setLayout(platform_layout)
        self.layout.addWidget(platform_box)

        # Genre selector
        self.genres_input = QLineEdit()
        self.genres_input.setPlaceholderText("Genres (comma-separated)")
        self.layout.addWidget(QLabel("Preferred Genres:"))
        self.layout.addWidget(self.genres_input)

        # Developer input
        self.dev_input = QLineEdit()
        self.dev_input.setPlaceholderText("Developer(s) (comma-separated)")
        self.layout.addWidget(QLabel("Preferred Developers:"))
        self.layout.addWidget(self.dev_input)

        # Publisher input
        self.pub_input = QLineEdit()
        self.pub_input.setPlaceholderText("Publisher(s) (comma-separated)")
        self.layout.addWidget(QLabel("Preferred Publishers:"))
        self.layout.addWidget(self.pub_input)

        # Liked games input
        self.liked_input = QLineEdit()
        self.liked_input.setPlaceholderText(
            "Game Tile(s)  (comma-separated)")
        self.layout.addWidget(
            QLabel("Games You Already Like:"))
        self.layout.addWidget(self.liked_input)

        # Critic/User toggle
        self.critic_checkbox = QCheckBox("Prefer critic score over user score")
        self.critic_checkbox.setChecked(True)
        self.layout.addWidget(self.critic_checkbox)

        # Button
        self.recommend_button = QPushButton("Get Recommendations")
        self.recommend_button.clicked.connect(self.get_recommendations)
        self.layout.addWidget(self.recommend_button)

        # Results display
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.layout.addWidget(QLabel("Top Recommendations:"))
        self.layout.addWidget(self.results_area)

        self.setLayout(self.layout)

    def get_recommendations(self):
        age = int(self.age_input.text()) if self.age_input.text().isdigit() \
            else 18
        platforms = [name for name, cb in self.platform_checkboxes.items()
                     if cb.isChecked()]

        genres = [g.strip() for g in self.genres_input.text().split(",")
                  if g.strip()]
        devs = [d.strip() for d in self.dev_input.text().split(",")
                if d.strip()]
        pubs = [p.strip() for p in self.pub_input.text().split(",")
                if p.strip()]
        prefer_critic = self.critic_checkbox.isChecked()
        liked_games = [g.strip() for g in self.liked_input.text().split(",") if
                       g.strip()]

        results = recommend_games_from_metacritic(
            user_age=age,
            platform_filter=platforms if platforms else None,
            preferred_genres=genres if genres else None,
            preferred_developers=devs if devs else None,
            preferred_publishers=pubs if pubs else None,
            prefer_critic_over_user=prefer_critic,
            liked_games=liked_games if liked_games else None
        )

        self.results_area.clear()
        for game in results:
            title = game["title"]
            score = round(game["score"], 2)
            platforms = ", ".join(game["platforms"]) if game.get(
                "platforms") else "N/A"
            self.results_area.append(
                f"{title} — Score: {score}\nPlatforms: {platforms}\n\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameRecommenderUI()
    window.show()
    sys.exit(app.exec_())
