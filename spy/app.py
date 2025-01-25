
from flask import Flask, render_template, request, session, redirect, url_for
import random
import uuid

app = Flask(__name__)
app.secret_key = "spy_game_secret"

# List of words for the game
words = ["apple", "banana", "car", "house", "computer", "dog", "phone", "tree"]

# Store active game rooms in memory (for simplicity)
game_rooms = {}

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action = request.form.get("action")
        game_id = request.form.get("game_id")

        if action == "create":
            new_game_id = str(uuid.uuid4())  # Generate a unique Game ID
            game_rooms[new_game_id] = {"players": [], "status": "waiting"}
            return redirect(url_for("lobby", game_id=new_game_id))

        elif action == "join":
            if game_id in game_rooms and len(game_rooms[game_id]["players"]) < 4:
                return redirect(url_for("lobby", game_id=game_id))
            else:
                return "Invalid game ID or game is full"

    return render_template("index.html")


@app.route("/lobby/<game_id>", methods=["GET", "POST"])
def lobby(game_id):
    if game_id not in game_rooms:
        return "Game ID not found"

    game = game_rooms[game_id]
    if len(game["players"]) < 4:
        if request.method == "POST":
            player_name = request.form.get("name")
            if player_name and player_name not in game["players"]:
                game["players"].append(player_name)
                if len(game["players"]) == 4:
                    # Assign words once 4 players join
                    assign_words(game)
                    return redirect(url_for("game", game_id=game_id))

        return render_template("lobby.html", game_id=game_id, players=game["players"])

    return redirect(url_for("game", game_id=game_id))


@app.route("/game/<game_id>", methods=["GET", "POST"])
def game(game_id):
    if game_id not in game_rooms:
        return "Game ID not found"

    game = game_rooms[game_id]
    if len(game["players"]) < 4:
        return redirect(url_for("lobby", game_id=game_id))

    # Determine the round and assign the current player
    round_number = len(game["players"])  # For simplicity, assume round is based on number of players
    current_player = game["players"][round_number % 4]
    current_word = game["words"][current_player]

    return render_template("game.html", game_id=game_id, current_player=current_player, word=current_word)


def assign_words(game):
    """Assign words to players and pick a spy."""
    spy_index = random.randint(0, 3)  # Random spy
    spy_word = random.choice(words)  # Spy's word is different
    players_words = random.sample(words, 3)  # 3 players get the same word

    game["words"] = {}
    for i, player in enumerate(game["players"]):
        if i == spy_index:
            game["words"][player] = spy_word  # Spy gets a different word
        else:
            game["words"][player] = random.choice(players_words)  # Non-spy players get the same word


if __name__ == "__main__":
    app.run(debug=True)
