# youtube-playlist-downloader
Download audio from all videos of any YouTube playlist (only works with new youtube design).

Add your playlist url in the /data/config.py file. Also add the chromedriver.exe to the /data/ path. Can be downloaded from the official website ([https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)).

Script will open the url in the chromium browser then scroll to the bottom to catch all videos. 
Afterwards it parses the html source code and retrieves video titles and individual video urls. 
Videos will then be downloaded using the 'youtube_dl' library.

The metadata of the downloaded audio files can then be customized using the GUI from my other repository (Repository &rarr; [Set metadata of mp3 files](https://github.com/RichardStelzer/set-metadata-of-mp3-files)).
