"""
Download audio from all videos in any YouTube playlist (only works with new youtube design (31.10.22))
"""

import os
import sys
import time
import youtube_dl
from bs4 import BeautifulSoup
from selenium import webdriver
import logging
import traceback

from data import config  # import custom config


def infinite_scroll(driver):
    # https://stackoverflow.com/questions/28928068/scroll-down-to-bottom-of-infinite-page-with-phantomjs-in-python/28928684#28928684
    scroll_pause_time = 1

    # get scroll height
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # scroll down to bottom
        driver.execute_script('window.scrollTo(0, ' + str(last_height) + ');')

        # wait to load page
        time.sleep(scroll_pause_time)

        # calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script('return document.documentElement.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height


def main():
    # open playlist url in chromium browser
    driver = webdriver.Chrome(executable_path=config.chromium_path, options=config.options)
    driver.get(config.playlist_url)  #
    time.sleep(0.05)

    # Accept cookies
    driver.find_element_by_xpath("//button[@aria-label='Alle akzeptieren']").click()

    time.sleep(0.05)

    # scroll to bottom of page, so all videos in playlist are visible
    infinite_scroll(driver)

    # retrieve source code and parse with a html parser
    source_code = driver.page_source
    soup = BeautifulSoup(source_code, "html.parser")  #
    domain = "https://www.youtube.com"

    driver.close()

    try:
        # search for channel name, channel url and playlist title
        content = soup.find("div", {"class": "metadata-wrapper"})
        playlist_title = content.find("yt-formatted-string", {"id": "text"}).text

        channel_info = content.find("yt-formatted-string", {"id": "owner-text"})
        channel_name = channel_info.text
        playlist_channel_url = channel_info.next.attrs["href"]

        playlist_general_information = {
            "channel_name": channel_name,
            'channel_url': domain + playlist_channel_url,
            'playlist_title': playlist_title
        }

        # create directory for playlist if it does not exist
        directory = os.path.join(os.getcwd(), "output", playlist_title, "text")
        if not os.path.exists(directory):
            os.makedirs(directory)

        # create text file with gathered metadata of all videos
        filename = directory + "\\" + playlist_title + "_full.txt"
        f = open(filename, "a", encoding="utf-8")
        f.truncate(0)  # clear file

        title_url_list = [["Video Title", "Video URL"]]

        for link in soup.find_all("a", {"class": "yt-simple-endpoint style-scope ytd-playlist-video-renderer"}):
            url = link.attrs["href"]
            if url.startswith("/watch?"):
                cropped_url = url.strip().split("&")[0]  # crop playlist url part off
                url = domain + cropped_url
                title = link.text
                # find('span', {'id': 'video-title'})
                # title = video_title.attrs['title']
                # replace strings in playlist names so result is compatible as file name
                title = title.replace("\n", "").strip()
                for r in ((" ", "_"), ("/", "-"), (",", "_"), ("\n", "")):
                    title = title.replace(*r)
                title_url_list.append([title, url])
                f.write(title + "   " + url + "\n")  # write video information to new line in the text file
            else:
                print("URL is not of correct form")
        f.close()
    except AttributeError:
        print("Parsed code not found.")  # only newest YouTube layout is parsable with this script
        ui_try_again = input("Try again? [Y/N]")
        if ui_try_again.lower() == "y":
            return True
        else:
            sys.exit()
    # except Exception as e:
    #     logging.error(traceback.format_exc())
    #     sys.exit()

    # create directories if they do not exist already
    directory_text = os.path.join(os.getcwd(), "output", playlist_title, "text")
    directory_audio = os.path.join(os.getcwd(), "output", playlist_title, "audio")
    directory_video = os.path.join(os.getcwd(), "output", playlist_title, "video")  # TODO, video is not downloaded, only audio
    directory_archive = os.path.join(os.getcwd(), "output", playlist_title, "archive")  # TODO, archive not implemented
    if not os.path.exists(directory_video):
        os.makedirs(directory_video)
    if not os.path.exists(directory_audio):
        os.makedirs(directory_audio)
    if not os.path.exists(directory_text):
        os.makedirs(directory_text)
    if not os.path.exists(directory_archive):
        os.makedirs(directory_archive)

    video_count = len(title_url_list)

    faulty_entries = []
    for idx, val in enumerate(title_url_list[1:]):  # start at second element
        print("\nCurrent Youtube Video = ", val)
        title = val[0]
        url = val[1]
        print("Output Directory: ", directory_audio)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": directory_audio + "/" + title + ".%(ext)s",
            "download_archive": directory_archive + "/" + title + ".%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("{} of {} already processed".format(idx + 1, video_count))
        except:
            faulty_entries.append(title_url_list.index(val))
            print("!!!! Error downloading with youtube-dl !!!!")

    print("Faulty Youtube Videos, (deleted, copyright issues etc.): ", faulty_entries)

    filename = directory_text + "\\" + playlist_title + "_faulty.txt"  # create text file containing the faulty video list
    f = open(filename, "a", encoding="utf-8")
    f.truncate(0)  # clear file

    for item in sorted(faulty_entries,
                       reverse=True):  # remove faulty entries from the list containing all playlist video information
        temp = title_url_list[item][0] + '        ' + title_url_list[item][1]
        f.write("%s\n" % temp)  # add faulty video to text file
        del title_url_list[item]  # delete faulty entry from list
    f.close()

    # create text file containing only successfully downloaded playlist entries
    filename = directory_text + "\\" + playlist_title + "_cleaned.txt"
    f = open(filename, 'a', encoding='utf-8')
    f.truncate(0)  # clear file

    for item in title_url_list:
        temp = item[0] + '        ' + item[1]
        f.write("%s\n" % temp)
    f.close()


if __name__ == "__main__":
    restart = True
    # start again, if browser loaded old YouTube design (only the new design is parsable with this script)
    while restart is True:
        restart = main()
