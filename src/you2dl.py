import os
import json
import yt_dlp
import selenium
import selenium.webdriver
import time
import tempfile
import subprocess
import pathlib
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def search(keyword, channel=None, limit=10, ignore_words=None):

    # Start headless Google Chrome
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
       
    options.add_experimental_option('w3c', True)
    
    driver = selenium.webdriver.Chrome(options=options)

    
    url = 'https://www.youtube.com'
    driver.get(url)
    driver.add_cookie({'name': 'CONSENT', 'value': 'YES+1',
                       'domain': '.youtube.com'})
    
    
    # perform actual search
    search_text = '+'.join(keyword)
    if channel is not None:
        url = 'https://www.youtube.com/c/' + channel + '/search?query=' \
            + search_text
    else:
        url = 'https://www.youtube.com/results?search_query=' + search_text

    driver.get(url)
   
  
    # Infinite scroll until we get the number of videos we want
    load_time = 0.5  # seconds
    videos_per_page = 6

    for i in range(limit // videos_per_page + 1):
        html = driver.find_element(By.TAG_NAME,'html')
        html.send_keys(selenium.webdriver.common.keys.Keys.END)
        time.sleep(load_time)
    
    # Get video link

    #driver.switch_to.frame
    results = driver.find_elements(By.XPATH,'//*[@id="video-title"]')
    results = [result for result in results if all(word.lower() in result.get_attribute('title').lower() for word in keyword)]
    print(results[0].get_attribute('title').lower())

    if ignore_words is not None:
        results = [result for result in results if all(word not in result.get_attribute('title') for word in ignore_words)]

    links = []
    for i in results:
        links.append(i.get_attribute('href'))
    links = links[:limit]
    

    links = list(filter(None, links))
    links = list(set(links))
    return links


def shell(cmd):



    # Run command
    os.system(cmd)
    '''
    # Read command output from logfile
    fd = open(tmp_log_file, 'r')
    output = fd.read()
    fd.close()

    # Delete log file
    os.remove(tmp_log_file)
    '''
    return 0





def download(url, dest_path, cookies=None, attempts=3, skip_video=False, skip_description=True, without_audio=False, audio_separated=False, audio_only=False, cmd = 'yt-dlp'):

    if not without_audio:
        cmd += ' -f "best[ext!=webm][width>=1920]/best[ext!=webm]"'
    else:
        cmd += ' -f "bestvideo[ext!=webm][width>=1920]/bestvideo[ext!=webm]"'

    if not skip_description:
        cmd += " --write-description"

    if skip_video:
        cmd += " --skip-download --youtube-skip-dash-manifest"

    # Add output path option
    path = os.path.join(dest_path, '%(title)s-%(id)s.%(ext)s') 
    audio_path = os.path.join(dest_path, '%(title)s-%(id)s.mp3')
    cmd += ' -o "' + path + '"'

    # Add cookie file path option
    if cookies is not None:
        cmd += ' --cookies "' + cookies + '"'
    
    #add URL
    cmd += ' "' + url + '"'  
    
    #yt-dlp to download video or audio
    success = False
    retcode = -1
    if audio_only:
        shell("yt-dlp"+' -f "bestaudio"'+' -o "' + audio_path + '"'+' --cookies "' + cookies + '"'+' -x --audio-format mp3'+' "' + url + '"')
    else:
        while attempts > 0 and not success: 
            attempts -= 1
            retcode = shell(cmd)
            success = True if retcode == 0 else False
   
    # if needed, save as an extra audio file
    if audio_separated:
       shell("yt-dlp"+' -f "bestaudio"'+' -o "' + audio_path + '"'+' --cookies "' + cookies + '"'+' -x --audio-format mp3'+' "' + url + '"')


    return retcode


def extract_youtube_video_code_from_fname(fname):

    return fname[-15:].split('.')[0]


def extract_youtube_video_code_from_url(url: str, video_code_len: int = 11):

    return url[-video_code_len:]


def find_all_videos(path: str, extensions: list = ['*.mp4']):

    already_downloaded = []
    for path in pathlib.Path(path).rglob('|'.join(extensions)):
        already_downloaded.append(extract_youtube_video_code_from_fname(path.name))
    return already_downloaded

def find_all_videos_byjson(path: str):

    already_downloaded = []
    with open(path,'r') as file:
        dict = json.load(file)
        for vid in dict:
            already_downloaded.append(vid['youtubeId'])

    return already_downloaded


def prune_video_list(urls: list, discard: list, 
        youtube_addr: str = 'https://www.youtube.com/watch?v=') -> list:

    # The list of urls must not be empty
    assert(urls)
    print(urls)

    # The list of videos to be discarded 
    if not discard:
        print('[WARN] No previous videos were detected.')
    
    # Convert the list of -already downloaded- video codes to a set 
    prev_codes = set(discard)

    # Convert URLs to video codes
    new_codes = set([extract_youtube_video_code_from_url(x) for x in urls])

    # Filter out those new codes that we have already downloaded
    new_codes = new_codes - new_codes.intersection(prev_codes)
    new_list_of_urls = [youtube_addr + x for x in list(new_codes)]

    return new_list_of_urls


if __name__ == '__main__':
    raise RuntimeError('[ERROR] This module, you2dl, cannot run as a script.')
