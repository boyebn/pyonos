__author__ = 'boye'

from boye import Spotify
from flask import Flask, url_for, redirect, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/playlist')
@app.route('/playlist/<uri>')
def home(uri='spotify:user:pumazz:playlist:2e3fd32clPYmADf809LrM6'):

    playlist = spotify.get_playlist(uri)

    if spotify.Queue.has_next():
        current = spotify.Queue.get_current()['track'].name
        return render_template('playlist.html', now_playing=current, playlist=playlist)

    return render_template('playlist.html', playlist=playlist)

@app.route('/queue/<uri>')
def add_queue(uri):
    spotify.Queue.add_queue(uri)
    return redirect(url_for('home'))

@app.route('/next/<uri>')
def add_next(uri):
    spotify.Queue.add_next(uri)
    return redirect(url_for('home'))

@app.route('/now/<uri>')
def play_now(uri):
    spotify.Queue.add_next(uri)
    spotify.Player.play_next()
    return redirect(url_for('home'))

@app.route('/play')
def play():
    if not spotify.Player.is_loaded():
        spotify.Player.restart()
    else:
        spotify.Player.play()
    return redirect(url_for('home'))

@app.route('/pause')
def pause():
    if spotify.Player.is_loaded():
        spotify.Player.pause()
    return redirect(url_for('home'))

if __name__ == '__main__':
    spotify = Spotify()
    app.run(debug=True)