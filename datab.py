import sqlite3


class Database:

	def __init__(self,persistentConn = True):
		self.persistentConn = persistentConn
		if persistentConn:
			self.conn = sqlite3.connect('pyonos.db')
		
	
	def trackPlayed(self,uri):
		if not self.persistentConn:
			self.conn = sqlite3.connect('pyonos.db')
		cur = self.conn.execute('SELECT * FROM TRACKS where uri = "{}"'.format(uri))
		uris = cur.fetchone()
		if uris:
			self.conn.execute('UPDATE TRACKS SET NUM_PLAYS = {0} WHERE ID = {1}'.format(uris[2]+1,uris[0]))
			self.conn.commit()
		else:
			self.conn.execute('INSERT INTO TRACKS (URI) VALUES ("{0}")'.format(uri))
			self.conn.commit()
		if not self.persistentConn:
			self.conn.close()
	
	def getTopTracks(self,num):
		if not self.persistentConn:
			self.conn = sqlite3.connect('pyonos.db')
		cur = self.conn.execute('select uri, num_plays from tracks order by num_plays desc limit {}'.format(num))
		return cur.fetchall()
		if not self.persistentConn:
			self.conn.close()

	def delTrack(self,uri):
		if not self.persistentConn:
			self.conn = sqlite3.connect('pyonos.db')
		self.conn.execute('delete from tracks where uri = "{}"'.format(uri))
		self.conn.commit()
		if not self.persistentConn:
			self.conn.close()
	
	def listPlayed(self,uri):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                cur = self.conn.execute('SELECT * FROM playlists where uri = "{}"'.format(uri))
                uris = cur.fetchone()
                if uris:
                        self.conn.execute('UPDATE playlists SET NUM_PLAYS = {0} WHERE ID = {1}'.format(uris[2]+1,uris[0]))
                        self.conn.commit()
                else:
                        self.conn.execute('INSERT INTO playlists (URI) VALUES ("{0}")'.format(uri))
                        self.conn.commit()
                if not self.persistentConn:
                        self.conn.close()

        def getTopLists(self,num):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                cur = self.conn.execute('select uri, num_plays from playlists order by num_plays desc limit {}'.format(num))
                return cur.fetchall()
                if not self.persistentConn:
                        self.conn.close()

        def delList(self,uri):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                self.conn.execute('delete from playlists where uri = "{}"'.format(uri))
                self.conn.commit()
                if not self.persistentConn:
                        self.conn.close()

	def albumPlayed(self,uri):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                cur = self.conn.execute('SELECT * FROM album where uri = "{}"'.format(uri))
                uris = cur.fetchone()
                if uris:
                        self.conn.execute('UPDATE album SET NUM_PLAYS = {0} WHERE ID = {1}'.format(uris[2]+1,uris[0]))
                        self.conn.commit()
                else:
                        self.conn.execute('INSERT INTO album (URI) VALUES ("{0}")'.format(uri))
                        self.conn.commit()
                if not self.persistentConn:
                        self.conn.close()

        def getTopAlbums(self,num):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                cur = self.conn.execute('select uri, num_plays from album order by num_plays desc limit {}'.format(num))
                return cur.fetchall()
                if not self.persistentConn:
                        self.conn.close()

        def delAlbum(self,uri):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                self.conn.execute('delete from album where uri = "{}"'.format(uri))
                self.conn.commit()
                if not self.persistentConn:
                        self.conn.close()

	def artistPlayed(self,uri):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                cur = self.conn.execute('SELECT * FROM artist where uri = "{}"'.format(uri))
                uris = cur.fetchone()
                if uris:
                        self.conn.execute('UPDATE artist SET NUM_PLAYS = {0} WHERE ID = {1}'.format(uris[2]+1,uris[0]))
                        self.conn.commit()
                else:
                        self.conn.execute('INSERT INTO artist (URI) VALUES ("{0}")'.format(uri))
                        self.conn.commit()
                if not self.persistentConn:
                        self.conn.close()

        def getTopArtists(self,num):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                cur = self.conn.execute('select uri, num_plays from artist order by num_plays desc limit {}'.format(num))
                return cur.fetchall()
                if not self.persistentConn:
                        self.conn.close()

        def delArtist(self,uri):
                if not self.persistentConn:
                        self.conn = sqlite3.connect('pyonos.db')
                self.conn.execute('delete from artist where uri = "{}"'.format(uri))
                self.conn.commit()
                if not self.persistentConn:
                        self.conn.close()

	def __del__(self):
		if self.persistentConn:
			self.conn.close()



if __name__ == '__main__':
	db = Database()
	db.trackPlayed('2WfaOiMkCvy7F5fcp2zZ8L')
	db.artistPlayed('2jzc5TC5TVFLXQlBNiIUzE')
	db.albumPlayed('0RfwViNsdcwjUgoZExOir0')
	db.listPlayed('0aqTfVhoVIm2Co6kHgzXsA')
	print db.getTopTracks(1)
	print db.getTopArtists(1)
	print db.getTopAlbums(1)
	print db.getTopLists(1)
	db.delTrack('2WfaOiMkCvy7F5fcp2zZ8L')
	db.delArtist('2jzc5TC5TVFLXQlBNiIUzE')
	db.delAlbum('0RfwViNsdcwjUgoZExOir0')
	db.delList('0aqTfVhoVIm2Co6kHgzXsA')
