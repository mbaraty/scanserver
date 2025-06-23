# Scanserver

My scanner is old. It is difficult to get it to scan to a pc. I also wanted to learn Django. Thus, I created Scanserver. The idea is simple: the scanner doesn't have a problem sending files to SMB shares, so I now scan to a share hosted on a vm then I have a nice web UI to download the files. We even use OCR to give the text to my own ollama server so that we can get nice short summaries. We can also choose whether to export the scan as a pdf or as a folder of jpegs.  
