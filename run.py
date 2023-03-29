import telebot
import openai
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import datetime


bot = telebot.TeleBot('telegram bot api')

openai.api_key = 'open ai api'
model_id = 'text-davinci-003'

client_id = 'spotify id'
client_secret = 'spotify secret'
client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
print("Bot ishga tushdi")


def generate_response(message):
    prompt = f'User: {message}\nAI:'
    response = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        max_tokens=64,
        n=1,
        stop=None,
        temperature=0.5,
    )
    print("User:", message)
    print("Bot: ", response.choices[0].text.strip())
    return response.choices[0].text.strip()
    


@bot.message_handler(commands=['spotify'])
def search_spotify(message):
    search_query = message.text.replace('/spotify ', '')
    
    results = spotify.search(q=search_query, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_info = f"{track['name']} tomonidan {track['artists'][0]['name']} albomdan {track['album']['name']}"
        response = f"Spotifyda nima topdim:\n\n{track_info}"
    else:
        response = f"Sorry, I couldn't find anything for '{search_query}' on Spotify."
    
    bot.reply_to(message, response)

def get_track_info(track_name):
    results = spotify.search(q=track_name, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_info = f"{track['name']} by {track['artists'][0]['name']} from the album {track['album']['name']}"
    else:
        track_info = "Kechirasiz, men bu trek haqida ma'lumot topa olmadim."
    return track_info


def get_artist_info(artist_name):
    results = spotify.search(q=artist_name, type='artist')
    if results['artists']['items']:
        artist = results['artists']['items'][0]
        artist_info = f"{artist['name']} is a {artist['genres'][0]} artist with {artist['followers']['total']} followers on Spotify."
    else:
        artist_info = "Kechirasiz, men o'sha rassom haqida ma'lumot topa olmadim."
    return artist_info


def get_album_info(album_name):
    results = spotify.search(q=album_name, type='album')
    if results['albums']['items']:
        album = results['albums']['items'][0]
        album_info = f"{album['name']} by {album['artists'][0]['name']} with {album['total_tracks']} tracks"
    else:
        album_info = "Kechirasiz, men bu albom haqida ma'lumot topa olmadim."
    return album_info


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom, men ChatGPTga ulanganman va Spotify-da treklar, rassomlar va albomlar haqida ma'lumot beradigan botman. Sizni qiziqtirgan trek, ijrochi yoki albom nomini kiriting!")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, "Camandalar: \n /spotify (musica,qoshiqchi,yoki albom)")



@bot.message_handler(func=lambda message: True)
def respond_to_message(message):
    response = generate_response(message.text)
    
    with open('messages.txt', 'a') as f:
        f.write(f"{datetime.datetime.now()} - User {message.from_user.id}: {message.text}\n")
        f.write(f"{datetime.datetime.now()} - Bot: {response}\n")
    
    if 'track:' in response:
        track_name = response.split('track:')[1].strip()
        track_info = get_track_info(track_name)
        bot.send_message(message.chat.id, track_info)
    elif 'artist:' in response:
        artist_name = response.split('artist:')[1].strip()
        artist_info = get_artist_info(artist_name)
        bot.send_message(message.chat.id, artist_info)
    elif 'album:' in response:
        
        album_name = response.split('album:')[1].strip()
        album_info = "Albom: "+get_album_info(album_name) 
        
        bot.send_message(message.chat.id, album_info)
    else:
        bot.send_message(message.chat.id, response)

bot.polling()