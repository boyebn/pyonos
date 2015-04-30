from flask import Flask, request, url_for
import json
import urllib2
import urllib



app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World, bitches!'


@app.route('/bitch/<search>')
def bitch(search):
    URL = 'https://api.spotify.com/v1/search?q=' + str(search) + '&type=artist'
    URL = urllib.quote_plus(URL,safe="%/:=&?~#+!$,;'@()*[]")
    site = urllib2.urlopen(URL)
    data = json.load(site)

    result = list()

    for artist in data['artists']['items']:

        if artist['images']:
            image = artist['images'][-1]['url']
        else:
            image = 'http://placehold.it/200x200'
        #top_track_url = 'https://api.spotify.com/v1/artists/'+ artist['id'] +'/top-tracks?country=NO'
        result.append('Name: {} <br />'
                      'Bilde: <img src="{}" alt="et bilde" style="width:200px;height:200px"><br />'
                     'URL: {}<br />' '<a href="{}">Ga til Artist</a><br />'.format(artist['name'], image,
                                      artist['external_urls']['spotify'],url_for('top',id=artist['id'])))

    return '<br /><br />'.join(result)

@app.route('/bitch/artist/<id>')
def top(id):
    artist_url = 'https://api.spotify.com/v1/artists/' + id
    artist_site = urllib2.urlopen(artist_url)
    artist_data = json.load(artist_site)
    if artist_data['images']:
        img_url = artist_data['images'][0]['url']
    name = artist_data['name']
    top_track_url = 'https://api.spotify.com/v1/artists/'+ id +'/top-tracks?country=NO'
    top_site = urllib2.urlopen(top_track_url)
    top_data = json.load(top_site)
    top_names = list()
    for track in top_data['tracks']:
        top_names.append(track['name'])

    result = list()
    result.append('<font size="20">{}</font><br />'
                  '<img src="{}" alt="et bilde" style="width:500px;height:500px"><br />'
                  'top tracks:<br />'
                  '{}<br />'.format(name,img_url,'<br />'.join(top_names)))

    return '<br /><br />'.join(result)


@app.route('/form')
def form():







if __name__ == '__main__':
    app.run(debug=True)
