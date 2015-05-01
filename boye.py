# coding=utf-8

__author__ = 'boye'

import spotify
import threading
import settings


class Player(object):

    def __init__(self, session, queue):
        audio = spotify.AlsaSink(session)
        self.queue = queue
        self.session = session

        # Login
        logged_in_event = threading.Event()

        def connection_state_listener(session):
            if session.connection.state is spotify.ConnectionState.LOGGED_IN:
                logged_in_event.set()

        self.session.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            connection_state_listener
        )
        self.session.login(settings.SPOTIFY_USER, settings.SPOTIFY_PASS)

        while not logged_in_event.wait(0.1):
            self.session.process_events()  # waits until the login is complete

        self.session.on(spotify.SessionEvent.END_OF_TRACK, self.play_next())

    def get_track(self, track_url):
        return self.session.get_track(track_url).load()

    def is_loaded(self):
        return not self.session.player.state == spotify.PlayerState.UNLOADED

    def stop(self):
        self.session.player.unload()

    def pause(self):
        self.session.player.pause()

    def play(self):
        self.session.player.play()

    def play_next(self):
        self.stop()
        if not self.queue.has_next():
            return
        track = self.queue.get_next()['track']
        self.session.player.load(track)
        self.session.player.play()

    def play_previous(self):
        self.stop()
        if self.queue.has_previous():
            track = self.queue.get_previous()['track']
        else:
            track = self.queue.get_current()['track']
        self.session.player.load(track)
        self.session.player.play()

    def restart(self):
        self.stop()
        track = self.queue.get_current()
        if not track:
            return
        self.session.player.load(track['track'])
        self.session.player.play()

    def print_track(self, track):
        name = str(track.name)
        artists = [str(artist.name) for artist in track.artists]
        album = str(track.album.name)
        length = int(track.duration)

        print '''
        Låt: {0}
        Artist(er): {1}
        Album: {2}
        Lengde (ms): {3}
        '''.format(name, ', '.join(artists), album, length)


class PlayQueue(object):
    def __init__(self, session):
        assert isinstance(session, spotify.Session)

        self.session = session
        self.queue = list()
        self.position = 0
        self.queue_size = 0

    def get_next(self):
        """ Returns next song in queue if any, false otherwise """
        if self.queue:
            self.position = (self.position + 1) % self.queue_size
            track = self.queue[self.position]

            return track

        return False

    def get_current(self):
        if self.queue:
            return self.queue[self.position]
        return False

    def get_previous(self):
        if self.queue:
            self.position = (self.position - 1) % self.queue_size
            track = self.queue[self.position]

            return track

        return False

    def has_next(self):
        return self.queue_size > 0

    def has_previous(self):
        return self.queue_size > 0

    def add_queue(self, track_url):
        """ Queue a song, track_url on the form: spotify:track:<track_id> """
        self.queue_size += 1
        self.queue.append({'url': track_url, 'track': self.session.get_track(track_url).load()})

    def add_next(self, track_url):
        """ Add a song to be played immediately after current song """
        self.queue_size += 1
        self.queue.insert(self.position + 1, {'url': track_url, 'track': self.session.get_track(track_url).load()})

    def remove(self, index):
        """ Removes song at the given index, returns True if successful, False otherwise """

        if not self.queue or index > self.queue_size - 1:
            return False

        if index > self.position:
            self.queue.pop(index)
            self.queue_size -= 1
            return True
        elif index < self.position:
            self.position -= 1
            self.queue.pop(index)
            self.queue_size -= 1
            return True
        else:
            return False

    def remove_current(self):
        """ Removes current song, returns next song if any, false otherwise """
        if self.queue:
            self.queue.pop(self.position)
            if self.queue:
                self.queue_size -= 1
                return self.queue[self.position]
        return False

    def get_queue(self):
        """ Returns the current queue """
        return self.queue

    def get_queue_urls(self):
        """ Returns a list containing the urls of the tracks in the queue """
        return [track['url'] for track in self.queue]

    def get_queue_tracks(self):
        """ Returns a list containing the track-objects of the tracks in the queue """
        return [track['track'] for track in self.queue]


class Spotify(object):
    def __init__(self):
        config = spotify.Config()
        config.user_agent = 'Svanborg Spotify Client'
        self.session = spotify.Session(config)
        self.session.preferred_bitrate(1)  # 320 kib/s

        self.Queue = PlayQueue(self.session)
        self.Player = Player(self.session, self.Queue)

    def get_playlist(self, uri):
        return self.session.get_playlist(uri).load()