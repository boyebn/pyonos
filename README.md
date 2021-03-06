# pyonos
_pyonos_ is a remotely controllable spotify client that can be installed on any system with python support and an 
ALSA-compatible soundcard. It can be accessed locally via an internet browser by navigating to the host's (the system 
running pyonos) local IP address with the proper port (e.g. 192.168.1.18:5001). From there you can play music in a 
priority queue. The website is both desktop- and mobile-friendly.

Main window (home):

![Main Window](img/pyonos_main.png)

Search window:

![Search Window](img/pyonos_search.png)

## Install
For this to work, it has to run on a computer with an ALSA-compatible soundcard (e.g. Raspberry PI). 
If no such soundcard exists, you have to modify the audio sink specified in the init-function of the boye.py's Player-class.

### Debian/Ubuntu/Raspbian
__Install libspotify__
```ShellSession
wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/mopidy.list
sudo apt-get update
sudo apt-get install libspotify-dev
```
__Install pyspotify__ (if pip complains about the '--pre' option, remove it)
```ShellSession
sudo apt-get install build-essential python-dev python3-dev libffi-dev
sudo pip install --pre pyspotify
```
__Install flask__
```ShellSession
sudo pip install Flask
```

__Install pyonos__
```ShellSession
git clone https://github.com/boyeborg/pyonos.git
```

## Setup

### Application key
You also need an application developer key from spotify.

* Go to the [Spotify developer pages](https://developer.spotify.com/) and login using your Spotify account.
* Find the [libspotify application keys management page](https://developer.spotify.com/technologies/libspotify/keys/) and request an application key for your application.
* Once the key is issued, download the “binary” version. The “C code” version of the key will not work with pyspotify.

Place the application key in root folder of pyonos (the same folder as app.py is in), and name it "spotify_appkey.key"

### Username and password
You have to make a settings.py-file in the root folder of pyonos (the same folder as app.py is in) containing your spotify username and password. It should look like this:
```Python
SPOTIFY_USER = 'username'
SPOTIFY_PASS = 'secret'
```
If you usaly use facebook for logging in to spotify, and don't know your spotify username, you can find this by going to your profile in the spotify desktop application, clicking on the option-button (scircle with three dots in it, right next to your profile picture), and copy the spotify URI. It will look something like this: `spotify:user:username` or `spotify:user:0123456789`. The part after "spotify:user:" is your username. You can probably [request a (new) password](https://www.spotify.com/no/password-reset/) for that username if you don't know it.


## Configure


### Port
On the bottom-most line of __app.py__ you can specify the port of the pyonos server
```Python
app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
```

### Front page playlists
The playlists displayed on the front page can be altered easily in __app.py__. Find the home-function, and add/remove playlist URIs in the list called "__pl__".
```Python
@app.route('/')
def home():
    pl = [
        'spotify:user:lars_93:playlist:17dahvTFovxEqqEJLsDoNQ',
        'spotify:user:pumazz:playlist:2e3fd32clPYmADf809LrM6',
        'spotify:user:pumazz:playlist:7dD8A6HTNUYW6kgs9yvh28',
        'spotify:user:lars_93:playlist:1cURhgTeJBdZFuurOcjFRg',
        'spotify:user:pumazz:playlist:2Qn3V38vhATTp1M7wzYG0p',
        'spotify:user:pumazz:playlist:6wnTPemhthfpExS1W8jklx',
        'spotify:user:magnode:playlist:5NLNeYg2ZMM8Zb1KR2mtBl'
    ]
```
For this to work, the playlist specified has to be public. You can make playlists public and find their URI in the spotify desktop application.

## Run
To run pyonos, simply:
```ShellSession
sudo python app.py
```
If you are running it on a server via ssh, and want to prevent it from stop running after the ssh session is terminated, you can either start it in a _screen_ like this:
```ShellSession
screen -S pyonos
sudo python app.py
```
And then detach from the screen with `ctrl+a+d`.
To reattach: 
```ShellSession
screen -r pyonos
```
To kill/stop/terminate pyonos:
```ShellSession
sudo fuser -n tcp -k <port>
```
The port is 5001 if you have not changed it (see the [port configure section](#port)).

## Use
To access pyonos, visit the local ip of the host running the pyonos server, on the port specified in the [port configuration](#port), in your internet browser (IE is not well supported). E.g.: 192.168.1.18:5001
