# youtube-playlist-downloader
Download audio from all videos of any YouTube playlist (only works with new youtube design).

Add your playlist url in the /data/config.py file. Also add the chromedriver.exe to the /data/ path.

Script will open the url in the chromium browser then scroll to the bottom to catch all videos. 
Afterwards it parses the html source code and retrieves video titles and individual video urls. 
Videos will then be downloaded using the 'youtube_dl' library.
