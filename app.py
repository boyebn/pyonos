import datetime

__author__ = 'boye'

from boye import Spotify
from flask import Flask, url_for, redirect, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/playlist')
@app.route('/playlist/<uri>')
def playlist(uri='spotify:user:pumazz:playlist:2e3fd32clPYmADf809LrM6'):

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

@app.route('/view/queue')
def view_queue():
    tracks = spotify.Queue.get_queue_tracks()

    return render_template('queue.html', tracks=tracks)

@app.route('/queue/remove/<uri>')
def remove_track(uri):
    uris = spotify.Queue.get_queue_urls()
    if uri == spotify.Queue.get_current()['url']:
        spotify.Queue.remove_current()
        spotify.Player.restart()
    else:
        i = uris.index(uri)
        if i >= 0:
            spotify.Queue.remove(i)

    return redirect(url_for('view_queue'))

@app.route('/search/user')
def user_search():
    return render_template('users.html')

@app.route('/album/<uri>')
def view_album(uri):
    album = spotify.get_album(uri)
    result = False

    track_list = list()

    for track in spotify.get_tracks_of_album(album):
        result = True
        track.load()
        name = track.name
        duration = '%d:%02d' % divmod(track.duration/1000, 60)
        if len(name) > 35:
            name = name[:30] + '...'
        artist = ', '.join([artist.name for artist in track.artists])
        if len(artist) > 35:
            artist = artist[:30] + '...'
        uri = track.link.uri

        track_list.append({"name": name, "artist": artist, "uri": uri, "duration": duration})

    name = album.name

    artist = album.artist.name

    image = album.cover_link().url

    return render_template('album.html', result=result, image=image, artist=artist, name=name, tracks=track_list)


@app.route('/search')
def search():
    try:
        s = request.args['s']
        result = spotify.search(s)

        artist_list = list()
        track_list = list()
        album_list = list()

        for artist in result.artists:
            artist.load()
            try:
                img = artist.portrait_link().url
            except AssertionError:
                # artist has no portrait
                img = 'http://placehold.it/300x300'
            name = artist.name
            if len(name) > 22:
                name = name[:20] + '...'
            uri = artist.link.uri

            artist_list.append({"image": img, "name": name, "uri": uri})

        for track in result.tracks:
            track.load()
            name = track.name
            duration = '%d:%02d' % divmod(track.duration/1000, 60)
            if len(name) > 35:
                name = name[:30] + '...'
            artist = ', '.join([artist.name for artist in track.artists])
            if len(artist) > 35:
                artist = artist[:30] + '...'
            uri = track.link.uri

            track_list.append({"name": name, "artist": artist, "uri": uri, "duration": duration})

        for album in result.albums:
            album.load()
            name = album.name
            if len(name) > 22:
                name = name[:20] + '...'
            artist = album.artist.name
            if len(artist) > 22:
                artist = artist[:20] + '...'
            uri = album.link.uri
            img = album.cover_link().url

            album_list.append({"name": name, "artist": artist, "uri": uri, "image": img})

        result = album_list or track_list or artist_list
        r = len(track_list)
        if r > 10:
            r = 10

        return render_template('search.html', song_range=range(r), result=result, search=s, albums=album_list,
                               tracks=track_list, artists=artist_list)

    except KeyError:
        return redirect(url_for('home'))

if __name__ == '__main__':
    spotify = Spotify()
    app.run(debug=True, host='0.0.0.0')