from flask import Flask, request
import json
import urllib2

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World, bitches!'

@app.route('/bitch/<artist>')
def bitch(artist):
    URL = 'https://api.spotify.com/v1/search?q=' + str(artist) + '&type=artist'
    site = urllib2.urlopen(URL)
    data = json.load(site)

    result = list()

    for artist in data['artists']['items']:
        if artist['images']:
            image = artist['images'][0]['url']
        else:
            image = 'http://placehold.it/200x200'
        result.append('Name: {} <br />'
                      'Bilde: <img src="{}" alt="et bilde"><br />'
                     'URL: {}'.format(artist['name'], image,
                                      artist['external_urls']['spotify']))

    return '<br /><br />'.join(result)

if __name__ == '__main__':
    app.run(debug=True)
