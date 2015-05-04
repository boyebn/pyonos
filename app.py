#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'boye'

from boye import Spotify
from time import sleep
import HTMLParser
from flask import Flask, url_for, redirect, render_template, request, Response
from gevent.wsgi import WSGIServer

app = Flask(__name__)


@app.route('/')
def home():
    pl = [
        'spotify:user:lars_93:playlist:17dahvTFovxEqqEJLsDoNQ',
        'spotify:user:pumazz:playlist:2e3fd32clPYmADf809LrM6',
        'spotify:user:pumazz:playlist:7dD8A6HTNUYW6kgs9yvh28',
        'spotify:user:lars_93:playlist:1cURhgTeJBdZFuurOcjFRg',
        'spotify:user:pumazz:playlist:2Qn3V38vhATTp1M7wzYG0p',
        'spotify:user:pumazz:playlist:6wnTPemhthfpExS1W8jklx'
    ]

    playlists = list()
    for uri in pl:
        playlist = spotify.get_playlist(uri)
        images = list()
        for track in playlist.tracks:
            track.load()
            if not track.availability == 1:
                continue
            try:
                url = track.album.load().cover_link(2).url
                images.append(url)
            except AssertionError:
                pass
            if len(images) >= 4:
                break

        while len(images) < 4:
            images.append("http://placehold.it/200x200")

        playlists.append({"name": playlist.name, "owner": playlist.owner.display_name, "uri": uri, "image": images})

    tracks = list()
    for track in spotify.Queue.get_queue_tracks():
        track.load()
        name = track.name
        duration = '%d:%02d' % divmod(track.duration / 1000, 60)
        if len(name) > 28:
            name = name[:25] + '...'
        artist = ', '.join([artist.name for artist in track.artists])
        if len(artist) > 35:
            artist = artist[:30] + '...'
        uri = track.link.uri

        tracks.append({"name": name, "artist": artist, "uri": uri, "duration": duration})

    return render_template('home.html', playlists=playlists, tracks=tracks)

@app.route('/playlist/<uri>')
def playlist(uri):
    pl = spotify.get_playlist(uri)

    tracks = list()
    images = list()

    for track in pl.tracks:
        track.load()
        if not track.availability == 1:
            continue
        if len(images) < 4:
            try:
                url = track.album.load().cover_link(2).url
                images.append(url)
            except AssertionError:
                pass
        name = track.name
        duration = '%d:%02d' % divmod(track.duration / 1000, 60)
        if len(name) > 35:
            name = name[:30] + '...'
        artist = ', '.join([artist.name for artist in track.artists])
        if len(artist) > 35:
            artist = artist[:30] + '...'
        track_uri = track.link.uri

        tracks.append({"name": name, "artist": artist, "uri": track_uri, "duration": duration})

    while len(images) < 4:
        images.append("http://placehold.it/200x200")

    return render_template('playlist.html', uri=uri, name=pl.name, owner=pl.owner.display_name, image=images, tracks=tracks)

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
        if not track.availability == 1:
            continue
        add_queue(track.load().link.uri)
    return ''

@app.route('/album/next/<uri>')
def add_next_album(uri):
    tracks = [track for track in spotify.get_tracks_of_album(spotify.get_album(uri))]
    if spotify.Queue.get_queue_size() <= 0:
        for track in tracks:
            track.load()
            if not track.availability == 1:
                continue
            add_queue(track.link.uri)
    else:
        tracks.reverse()
        for track in tracks:
            track.load()
            if not track.availability == 1:
                continue
            add_next(track.link.uri)
    return ''

@app.route('/album/now/<uri>')
def add_now_album(uri):
    add_next_album(uri)
    if spotify.Player.is_playing():
        spotify.Player.play_next()
    else:
        if spotify.Queue.get_queue_size() <= 0:
            spotify.Player.restart()
        else:
            spotify.Player.play_next()
    return ''

@app.route('/album/replace/<uri>')
def add_replace_album(uri):
    spotify.Queue.remove_all()
    add_queue_album(uri)
    spotify.Player.restart()
    return ''

@app.route('/playlist/queue/<uri>')
def add_queue_playlist(uri):
    tracks = spotify.get_playlist(uri).tracks
    for track in tracks:
        track.load()
        if not track.availability == 1:
            continue
        add_queue(track.link.uri)
    return ''

@app.route('/playlist/next/<uri>')
def add_next_playlist(uri):
    tracks = [track for track in spotify.get_playlist(uri).tracks]
    if spotify.Queue.get_queue_size() <= 0:
        for track in tracks:
            track.load()
            if not track.availability == 1:
                continue
            add_queue(track.link.uri)
    else:
        tracks.reverse()
        for track in tracks:
            track.load()
            if not track.availability == 1:
                continue
            add_next(track.link.uri)
    return ''

@app.route('/playlist/now/<uri>')
def add_now_playlist(uri):
    add_next_playlist(uri)
    if spotify.Player.is_playing():
        spotify.Player.play_next()
    else:
        if spotify.Queue.get_queue_size() <= 0:
            spotify.Player.restart()
        else:
            spotify.Player.play_next()
    return ''

@app.route('/playlist/replace/<uri>')
def add_replace_playlist(uri):
    spotify.Queue.remove_all()
    add_queue_playlist(uri)
    spotify.Player.restart()
    return ''

@app.route('/album/<uri>')
def view_album(uri):
    album = spotify.get_album(uri)
    result = False

    track_list = list()

    for track in spotify.get_tracks_of_album(album):

        track.load()
        if not track.availability == 1:
            continue

        result = True
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
            if not track.availability == 1:
                continue
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
    image, name, artist_browser = spotify.get_artist(uri)

    biography = artist_browser.biography

    top_tracks = list()

    for track in artist_browser.tophit_tracks:
        track.load()
        if not track.availability == 1:
            continue
        track_name = track.name
        duration = '%d:%02d' % divmod(track.duration / 1000, 60)
        if len(track_name) > 35:
            track_name = track_name[:30] + '...'
        artist = ', '.join([artist.name for artist in track.artists])
        if len(artist) > 35:
            artist = artist[:30] + '...'
        uri = track.link.uri

        top_tracks.append({"name": track_name, "artist": artist, "uri": uri, "duration": duration})

    albums = list()

    for album in artist_browser.albums:
        album.load()
        album_name = album.name
        if len(album_name) > 42:
            album_name = album_name[:40] + '...'
        artist = album.artist.name
        if len(artist) > 22:
            artist = artist[:20] + '...'
        uri = album.link.uri
        img = album.cover_link().url

        albums.append({"name": album_name, "artist": artist, "uri": uri, "image": img})

    return render_template('artist.html', albums=albums, num_of_albums=len(albums), tracks=top_tracks[:5], image=image, name=name,
                           biography=biography)


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
    user = spotify.get_user(uri)
    if user:
        name = user.display_name

        starred = list()

        for track in user.starred.load(2).tracks:
            track.load()
            if not track.availability == 1:
                continue
            track_name = track.name
            duration = '%d:%02d' % divmod(track.duration / 1000, 60)
            if len(track_name) > 35:
                track_name = track_name[:30] + '...'
            artist = ', '.join([artist.name for artist in track.artists])
            if len(artist) > 35:
                artist = artist[:30] + '...'
            uri = track.link.uri

            starred.append({"name": track_name, "artist": artist, "uri": uri, "duration": duration})

        playlists = list()

        for playlist in user.published_playlists.load():
            playlist.load()
            print playlist.name
            print playlist.link
            playlists.append({"name": playlist.name, "owner": playlist.owner, "subs": playlist.subscribers,
                              "uri": "hei"})

        return render_template('user.html', name=name, starred=starred, playlists=playlists)

    return render_template("user.html", name="No user", starred=list(), playlists=list())

@app.route('/play/index/<int:pos>')
def play_index(pos):
    spotify.Player.play_position(pos)
    return ''


if __name__ == '__main__':
    spotify = Spotify()
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
