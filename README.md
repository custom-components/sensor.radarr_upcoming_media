# Radarr Upcoming Media Component

Component required to use the associated Lovelace card: [Upcoming_Media_Card](https://github.com/custom-cards/upcoming-media-card)</br>
This is just a modified version of home assistants default sonarr (not a typo, modified from sonarr not radarr) component.</br>
This component works with or without the default radarr component.</br></br>
<link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/FgwNR2l"><img src="https://www.buymeacoffee.com/assets/img/BMC-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px">If you feel I deserve it, you can buy me a coffee</span></a>

## TODO:
1. Make a "banner" view with fanart images, poster only for now
2. Add genres as secondary info
3. Hide/show physical releases & cinema releases

## Installation:

1. Install this component by copying to your `/custom_components/sensor/` folder.
2. Add this to your `configuration.yaml` using the config options below example. 
3. **You will need to restart for the component to start working.**

```yaml
sensor:
- platform: radarr_upcoming_media
  api_key: YOUR_API_KEY
  host: 192.168.1.4
  port: 7878
  days: 120
  ssl: true
```

### Options

| key | default | required | description
| --- | --- | --- | ---
| api_key | | yes | Your Radarr API key
| host | localhost | no | The host Radarr is running on.
| port | 7878 | no | The port Radarr is running on.
| urlbase | / | no | The base URL Radarr is running under.
| days | 60 | no | How many days to look ahead for the upcoming sensor, 1 means today only.
| ssl | False | no | Whether or not to use SSL for Radarr. Set to `True` if you use SSL.

## Developers

**If you'd like to make your own component to feed the upcoming media card:**

1. Make a sensor that follows this naming convention "sensor.sonarr_upcoming_media", replacing sonarr with your service.
2. The state of the sensor must be the amount of items (episodes, movies, etc.) to be listed.
3. The card looks for numbered attributes with values formatted like these examples:

TV:
```
banner1: https://www.thetvdb.com/banners/graphical/5b43a197b530e.jpg
poster1: https://www.thetvdb.com/banners/_cache/posters/290853-15.jpg
title1: Fear the Walking Dead
subtitle1: Weak
airdate1: 2018-09-03T01:00:00Z
airtime1: 21:00
hasFile1: false
info1: S04E12
banner2: https://www.thetvdb.com/banners/graphical/239851-g.jpg
poster2: https://www.thetvdb.com/banners/_cache/posters/239851-2.jpg
title2: Penn & Teller: Fool Us
subtitle2: The Fool Us Zone
airdate2: 2018-09-04T00:00:00Z
airtime2: 20:00
hasFile2: false
info2: S05E11b
```
Movies:
```
poster1: ../local/custom-lovelace/upcoming-media-card/images/radarr/poster1.jpg
banner1: ../local/custom-lovelace/upcoming-media-card/images/radarr/banner1.jpg
title1: Solo: A Star Wars Story
subtitle1: 
airdate1: 2018-09-14T00:00:00Z
info1: Available 
hasFile1: false
poster2: ../local/custom-lovelace/upcoming-media-card/images/radarr/poster2.jpg
banner2: ../local/custom-lovelace/upcoming-media-card/images/radarr/banner2.jpg
title2: Patient Zero
subtitle2: 
airdate2: 2018-10-22T00:00:00Z
info2: Available 
hasFile2: false
```


Then all the user needs to do is put your service name in the config like so "service: sonarr".</br>
Please inform me if you create one and I'll add it to the list.</br>
If you need special styling or edits to the card to accomidate your service, just ask or submit a PR.</br></br>

Thanks!
