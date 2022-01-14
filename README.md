# bookgen

As a chess player, sometimes you wonder how to see all of your past games. Which variation you struggle with, what opening you love to play, or tricky moves that often trip you. Tailuge's [Opening Tree](https://tailuge.github.io/chess-o-tron/public/openings/openingtree.html) site is one of the perfect places to analyze your Lichess games. So, why not make its Chess.com version?

## How to
Writing JavaScript code for downloading and parsing Chess.com's PGN is difficult (at least for me). For now, you should use Python to run `main.py` to extract relevant information. That script will output `sample.json`, which can be viewed by running `python -m http.server` in terminal (or command prompt, or the like) and visiting [http://localhost:8000](http://localhost:8000) (default port). You should see page something like [this](https://kekavigi.github.io/bookgen/index.html). (That is me, playing rapid rated chess as white).

## To do
* "Translate" `main.py` to Javascript code, preferably without installing new thing just to run it.
* Add more control/customization for viewing result.
