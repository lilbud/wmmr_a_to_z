# wmmr_a_to_z

Every September, the radio station 93.3 WMMR in Philadelphia does a thing where to commerate the start of school, they play every song in their catalog in alphabetical order. Usually lasting a week or two during September. This year (2024) was the longest yet at 19 days and over 3k songs.

I wanted to try and catalog this list. I figured on grabbing the song list from WMMRs site, but the full list isn't published. They keep a day or two on their "recently played" page, then it disappears. Considering I didn't have this idea fully until last week, I was a bit late.

Luckily, I found a site called [TuneGenie](https://wmmr.tunegenie.com), which keeps a nearly full archive of all the songs played. Probably as complete as I can hope to get unless WMMR publishes their list.

## The process

While TuneGenie has all the data, they do not to my knowledge have an API of any kind. Also the site is loaded dynamically by hour using JS toggle elements. There are ways to trigger those while scraping but this was meant to be a smaller project. I ended up just activating the triggers from 6am-12am, going into inspect element and copying the whole HTML table.

After which I could take those HTML files, and parse them in Python to grab the song name, artist, and time played. Which could then be inserted into the database.

Is this an unnecessarily difficult way to do this? yes
Are there better ways to do this? also yes

## Why do this?

I was interested in the statistics of how many songs would be played. I think it might've been the realization how long the 'T' section would go considering they count songs with 'The' as 'T' (rather than the word after). As well as a breakdown of how many songs each day, and how many times an artist was represented.

This data is being provided as-is, as both a PostgreSQL database dump file, as well as a series of CSV files. Probably a better way to do it, but its nearly 2am at time of writing.
