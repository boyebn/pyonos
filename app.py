import datetime

__author__ = 'boye'

from boye import Spotify
from time import sleep
import json
from flask import Flask, url_for, redirect, render_template, request, Response
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue


class ServerSentEvent(object):
    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.iteritems() if k]

        return "%s\n\n" % "\n".join(lines)


app = Flask(__name__)


@app.route('/')
def home():
    users = [
        {'uri': 'spotify:user:lars_93', 'name': 'Lars'},
        {'uri': 'spotify:user:pumazz', 'name': 'Boye'},
        {'uri': 'spotify:user:magnode', 'name': 'Magnus'},
        {'uri': 'spotify:user:audun0104', 'name': "Audun"},
        {'uri': 'spotify:user:karlj0805', 'name': "Karl"},
        {'uri': 'spotify:user:1140694396', 'name': "Markus"}
    ]

    tracks = list()

    for track in spotify.Queue.get_queue_tracks():
        track.load()
        name = track.name
        duration = '%d:%02d' % divmod(track.duration / 1000, 60)
        if len(name) > 35:
            name = name[:30] + '...'
        artist = ', '.join([artist.name for artist in track.artists])
        if len(artist) > 35:
            artist = artist[:30] + '...'
        uri = track.link.uri

        tracks.append({"name": name, "artist": artist, "uri": uri, "duration": duration})

    return render_template('home.html', users=users, tracks=tracks)


# @app.route('/playlist')
#@app.route('/playlist/<uri>')
#def playlist(uri='spotify:user:pumazz:playlist:2e3fd32clPYmADf809LrM6'):
#
#    playlist = spotify.get_playlist(uri)
#
#    if spotify.Queue.has_next():
#        current = spotify.Queue.get_current()['track'].name
#        return render_template('playlist.html', now_playing=current, playlist=playlist)
#
#    return render_template('playlist.html', playlist=playlist)

@app.route('/queue/<uri>')
def add_queue(uri):
    spotify.Queue.add_queue(uri)
    return ''


@app.route('/next/<uri>')
def add_next(uri):
    spotify.Queue.add_next(uri)
    return ''


@app.route('/now/<uri>')
def play_now(uri):
    spotify.Queue.add_next(uri)
    spotify.Player.play_next()
    return ''


@app.route('/play')
def play():
    if not spotify.Player.is_loaded():
        spotify.Player.restart()
    else:
        spotify.Player.play()
    return ''


@app.route('/pause')
def pause():
    if spotify.Player.is_loaded():
        spotify.Player.pause()
    return ''


@app.route('/view/queue')
def view_queue():
    tracks = list()

    for track in spotify.Queue.get_queue_tracks():
        track.load()
        name = track.name
        duration = '%d:%02d' % divmod(track.duration / 1000, 60)
        if len(name) > 35:
            name = name[:30] + '...'
        artist = ', '.join([artist.name for artist in track.artists])
        if len(artist) > 35:
            artist = artist[:30] + '...'
        uri = track.link.uri

        tracks.append({"name": name, "artist": artist, "uri": uri, "duration": duration})

    return render_template('queue.html', tracks=tracks)

@app.route('/queue/remove/index/<int:pos>')
def remove_track_index(pos):
    if 0 <= pos <= spotify.Queue.get_queue_size() - 1:
        if pos == spotify.Queue.get_position():
            spotify.Queue.remove_current()
            if spotify.Player.is_playing():
                spotify.Player.restart()
            else:
                spotify.Player.restart()
                spotify.Player.pause()
        else:
            spotify.Queue.remove(pos)
    return ''

@app.route('/replace/<uri>')
def replace_queue_song(uri):
    spotify.Queue.remove_all()
    spotify.Queue.add_queue(uri)
    spotify.Player.restart()
    return ''

@app.route('/album/queue/<uri>')
def add_queue_album(uri):
    tracks = spotify.get_tracks_of_album(spotify.get_album(uri))
    for track in tracks:
        add_queue(track.load().link.uri)
    return ''

@app.route('/album/next/<uri>')
def add_next_album(uri):
    tracks = [track for track in spotify.get_tracks_of_album(spotify.get_album(uri))]
    if spotify.Queue.get_queue_size() <= 0:
        for track in tracks:
            track.load()
            add_queue(track.link.uri)
    else:
        tracks.reverse()
        for track in tracks:
            track.load()
            add_next(track.link.uri)
    return ''

@app.route('/album/now/<uri>')
def add_now_album(uri):
    add_next_album(uri)
    if spotify.Player.is_playing():
        spotify.Player.play_next()
    else:
        spotify.Player.play_next()
        spotify.Player.pause()
    return ''

@app.route('/album/replace/<uri>')
def add_replace_album(uri):
    spotify.Queue.remove_all()
    add_queue_album(uri)
    spotify.Player.restart()
    return ''


@app.route('/album/<uri>')
def view_album(uri):
    album = spotify.get_album(uri)
    result = False

    track_list = list()

    for track in spotify.get_tracks_of_album(album):
        result = True
        track.load()
        name = track.name
        duration = '%d:%02d' % divmod(track.duration / 1000, 60)
        if len(name) > 35:
            name = name[:30] + '...'
        artist = ', '.join([artist.name for artist in track.artists])
        if len(artist) > 35:
            artist = artist[:30] + '...'
        track_uri = track.link.uri

        track_list.append({"name": name, "artist": artist, "uri": track_uri, "duration": duration})

    name = album.name

    artist = album.artist.name

    image = album.cover_link(2).url

    return render_template('album.html', uri=uri, result=result, image=image, artist=artist, name=name,
                           tracks=track_list)


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
            duration = '%d:%02d' % divmod(track.duration / 1000, 60)
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


@app.route('/artist/<uri>')
def view_artist(uri):
    return render_template('artist.html')


@app.route('/stream/now_playing')
def stream_now_playing():
    def generate():
        old_index = -1
        while True:
            index = spotify.Queue.get_position()
            if old_index != index:
                old_index = index
                yield 'data: {}\n\n'.format(index)
            sleep(.1)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/stream/queue_changed')
def stream_queue_changed():
    def generate():
        while True:
            if spotify.Queue.is_changed():
                yield 'data: 1\n\n'
            sleep(.1)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/move/<int:index_from>/<int:index_to>')
def move_track(index_from, index_to):
    spotify.Queue.move(index_from, index_to)
    return ''


@app.route('/next')
def play_next():
    spotify.Player.play_next()
    return ''


@app.route('/previous')
def play_previous():
    spotify.Player.play_previous()
    return ''


@app.route('/user/<uri>')
def view_user(uri):
    return render_template('user.html')

@app.route('/play/index/<int:pos>')
def play_index(pos):
    spotify.Player.play_position(pos)
    return ''


if __name__ == '__main__':
    spotify = Spotify()
    app.run(debug=True, host='0.0.0.0', port=80, threaded=True)
