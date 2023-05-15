# heardle
# started 5/10/23

import time
from threading import Timer
import os 
import sys
import PIL
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtCore import *
import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pickle # used for storing data 
import random
import vlc 
import urllib.request
from PIL import Image

# handles user sign in (move to method)
client_uri = "http://google.com/callback"
client_id = "973f5e14396542ddae1b251bb8e99348"
client_secret = "4f723a9ba9614accbb803d07b2089c43"
# scope = "user-librar-read playlist-modify-public playlist-read-private"
oauth_object = spotipy.SpotifyOAuth(client_id, client_secret, client_uri)
token = oauth_object.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token)
user_name = sp.current_user()
saveData = {}

# handles save creation and user authorization 
class LoginScreen(QDialog):
  
  def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("mainui.ui", self)
        self.btnLogin.clicked.connect(self.login)
        
  def createSave(self):
    global saveName
    global filePath
    global saveData
    saveData = {"username":user, "wins":0, "losses":0,"numGames":0}
    saveName = user + "_save.dat"
    filepath = os.path.dirname(__file__) + saveName
    print(filepath)
    if(os.path.isfile(filepath) == False):
      print("save file being created")
      with open(saveName, 'wb') as f:
        pickle.dump(saveData, f)

  def loadSave(self):
    with open(saveName, 'rb') as f:
      saveData = pickle.load(f)
        
  def login(self): 
    global user
    user = self.inptUsername.text()
      
    if len(user) == 0:
      self.nameError.setText("Please enter a username.")
    else:
      self.createSave()
      self.loadSave()
      game = GameScreen()
      widget.addWidget(game)
      widget.setCurrentIndex(widget.currentIndex()+1)
      
      
      
class GameScreen(QDialog):
  
  def __init__(self):
      self.plays = 0
      self.winStatus = False
      self.uri = "4aMFXQuOBls98Ga62wKmba"
      self.guessCount = 0 
      super(GameScreen, self).__init__()
      loadUi("gamescreen.ui", self) 
      self.getSong()
      self.playButton.clicked.connect(self.playSong)
      self.userGuess.returnPressed.connect(lambda: self.checkGuess(self.plays))
      self.playButton.setDefault(False)
      self.btnSettings.clicked.connect(self.loadSettings)
      self.btnChartMode.clicked.connect(self.chartMode)

  def addPlays(self):
    self.plays += 1
        
        
  def getTrackArt(self, track_uri):
    songID = track_uri
    print(songID)
    track_info = sp.track(songID)
    albumID = track_info['album']['images'][0]['url']
    print(albumID)
    urllib.request.urlretrieve(albumID, "./trackart.png")
    
  def getSong(self):
    # uri = "0qpySfh1FiZHUq5jc1VYOJ"
    global song
    global artist
    global song_uri
    global preview_url
    tracks = [x["track"]["name"] for x in sp.playlist_tracks(self.uri)["items"]] # will only return first 100
    artists = [x["track"]["artists"][0]["name"] for x in sp.playlist_tracks(self.uri)["items"]] # will only return first 100
    track_uri = [x["track"]["uri"] for x in sp.playlist_tracks(self.uri)["items"]] # will only return first 100
    preview_urls = [x["track"]["preview_url"] for x in sp.playlist_tracks(self.uri)["items"]] # will only return first 100
    # cover_urls = [x["track"]["preview_url"] for x in sp.playlist_items(self.uri)["tracks"]] # will only return first 100
    while True:
      num = random.randint(0,len(tracks)-1)
      song = tracks[num]
      artist = artists[num]
      song_uri = track_uri[num]
      preview_url = preview_urls[num]
      if(preview_url != None):
        break
    self.getTrackArt(song_uri)
    
    print("song: " + song)
    print("artist(s): " + artist)
    print("song uri: " + song_uri)
    print("preview url: " + preview_url)
    
    # plays audio (will be moved when game is fully made)
    
    
  def checkPlays(self, plays):
    if(plays == 0):
      print("ran")
      return 3
    elif(plays == 1):
      return 6
    elif(plays == 2):
      return 9
    elif(plays == 3):
      return 12
    else:
      return 15
    
  def timer(self):
    global playTimer 
    playTimer = Timer(self.checkPlays(self.plays), self.stopSong)
    print(self.checkPlays(self.plays))
  
  def playSong(self):
    global p
    p = vlc.MediaPlayer(preview_url)
    p.play()
    self.timer()
    if(self.winStatus == False):
      playTimer.start()
  
  def stopSong(self):
    p.stop()

      
  def checkGuess(self, plays):
    plays = self.plays
    userGuess = self.userGuess.text()
    lowerGuess = userGuess.lower()
    wrongstyleSheet = "background-color:rgb(255, 64, 67); border-radius:12px; color: rgb(45, 45, 45); font:medium, 10pt 'Gotham'; padding:10px;"
    StyleSheet = "background-color:rgb(81, 215, 91); border-radius:12px; color: rgb(45, 45, 45); font:medium, 10pt 'Gotham'; padding:10px; "
    cSong = song.lower() 
    print(plays)
    if(lowerGuess not in cSong):
      print("incorrect")
      if(plays == 0):
        self.guess1.setStyleSheet(wrongstyleSheet)
        self.guess1.setText(userGuess)
        print(plays)
      elif(plays == 1):
        self.guess2.setStyleSheet(wrongstyleSheet)
        self.guess2.setText(userGuess)
      elif(plays == 2):
        self.guess3.setStyleSheet(wrongstyleSheet)
        self.guess3.setText(userGuess)
      elif(plays == 3):
        self.guess4.setStyleSheet(wrongstyleSheet)
        self.guess4.setText(userGuess)
      elif(plays == 4):
        self.guess5.setStyleSheet(wrongstyleSheet)
        self.guess5.setText(userGuess)
      else:
        self.endGame()
        print("you lose!")
        self.userGuess.setEnabled(False)
    else:
      if(plays == 0):
        self.guess1.setStyleSheet(StyleSheet)
        self.guess1.setText(song)
      elif(plays == 1):
        self.guess2.setStyleSheet(StyleSheet)
        self.guess2.setText(song)
      elif(plays == 2):
        self.guess3.setStyleSheet(StyleSheet)
        self.guess3.setText(song)
      elif(plays == 3):
        self.guess4.setStyleSheet(StyleSheet)
        self.guess4.setText(song)
      elif(plays == 4):
        self.guess5.setStyleSheet(StyleSheet)
        self.guess5.setText(song)
      self.userGuess.setEnabled(False)
      print("you win!")
      self.winStatus = True
      self.endGame()
    self.addPlays()
    self.userGuess.setText("")
    
  def loadSettings(self):
    self.s = Settings()
    self.s.show()
    
  def chartMode(self):
    self.uri = "https://open.spotify.com/playlist/37i9dQZEVXbLRQDuF5jeBp?si=112a506c6e15475b"
    self.getSong()
    
  # def moveWinBox(self, boxRef):
    
    
  def removeOtherGuesses(self):
    y_coord = 51
    guessBoxNum = self.plays + 1
    if(guessBoxNum == 1):
      self.guess2.hide()
      self.guess3.hide()
      self.guess4.hide()
      self.guess5.hide()
      guessBoxRef = self.guess1
    elif(guessBoxNum == 2):
      self.guess1.hide()
      self.guess3.hide()
      self.guess4.hide()
      self.guess5.hide()
      guessBoxRef = self.guess2
    elif(guessBoxNum == 3):
      self.guess2.hide()
      self.guess1.hide()
      self.guess4.hide()
      self.guess5.hide()
      guessBoxRef = self.guess3
    elif(guessBoxNum == 4):
      self.guess2.hide()
      self.guess3.hide()
      self.guess1.hide()
      self.guess5.hide()
      guessBoxRef = self.guess4
    else:
      self.guess2.hide()
      self.guess3.hide()
      self.guess4.hide()
      self.guess1.hide()
      guessBoxRef = self.guess5
    guessBoxRef.move(120, 90)
    while y_coord <= 211:
      y_coord += 1 
      guessBoxRef.resize(771, y_coord)
    widget.setCurrentIndex(widget.currentIndex()+1)
  
  def endGame(self):
    # add delay between widget opening 
    wlscrn = WinLossScreen()
    widget.addWidget(wlscrn)
    self.removeOtherGuesses()
    
    
  
  
  # def fadeScreen(self):
    
    
class Settings(QDialog):
  def __init__(self):
    super(Settings, self).__init__()
    loadUi("settings.ui", self) 
    self.btnApply.clicked.connect(self.changeSettings)
    global g 
    g = GameScreen()
    
  def changeSettings(self):
    playlist = self.userPlaylist.text()
    g.uri = playlist
    print(g.uri)
    g.getSong()
    

    

class WinLossScreen(QDialog):
  def __init__(self):
    super(WinLossScreen, self).__init__()
    loadUi("winorloss_scr.ui", self)
    pixmap = QPixmap('trackart.png')
    self.displayCover.setPixmap(pixmap)
    self.displayCover.setScaledContents(True)
    
    
      
      
        
     
app = QApplication(sys.argv)
welcome= LoginScreen()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(500)
widget.setFixedWidth(900)
widget.show()
try:
  sys.exit(app.exec_())
except:
  print()
  