# Web Server with custom video and audio player #


The video player supports subtittles and changing the audio track

Some browsers cannot play some video formats because this project is not using transcoding to convert in realtime the video/sound, it only converts the subtitles.

To change the audio track from a video you must need to enable "Experimental Web Platform features" in your browser.

Because of the limitations of HTLM5 it can only play webVTT subs but dont worry it will convert it automatically.



## Requirements: ##
 Python3, Windows/Linux, Flask, ffmpeg

 This software includes pysubs2 module under the MIT license
 you can find the complete LICENSE inside the zip file in app/data/pysubs2.zip


## To run the web server: ##
  - To run via flask internal HTTP server via CLI  
    ```python3 run.py -b IP_addr -p port -d directory [--dirsize]```

  - To use a WSGI for deployment -> (for example gunicorn)  
    ```gunicorn --env FOLDER=/PATH --env SHOWSIZE=True -b 127.0.0.1 app:app```



## API usage ##

To get the JSON you need to use curl or wget or send a request asking for a JSON.

For the text browsers and legacy browsers there is a custom html for better browsing (for lynx, links, w3m, ie explorer).

**To download a folder you must pass at the end of the dir path /?mode=dir to download it as tar.**

### To sort directory contents, add /?mode= followed by: ###

- *Sort type*
  - *s* for size
  - *n* for name
  - *d* for date

- *Sort direction*
  - *p* for ascending
  - *d* for descending

