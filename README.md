# Radarr Upcoming Media Component

Home Assistant component to feed [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card) with
Radarr's upcoming added media.</br>
This component does not require, nor conflict with, the default Radarr component.</br></br>
### Issues
Read through these two resources before posting issues to GitHub or the forums.
* [troubleshooting guide](https://github.com/custom-cards/upcoming-media-card/blob/master/troubleshooting.md)
* [@thomasloven's lovelace guide](https://github.com/thomasloven/hass-config/wiki/Lovelace-Plugins).



</br>
<a href="https://www.themoviedb.org/"><img width="200" src="https://www.themoviedb.org/assets/1/v4/logos/408x161-powered-by-rectangle-green-bb4301c10ddc749b4e79463811a68afebeae66ef43d17bcfd8ff0e60ded7ce99.png">
</br>This product uses the TMDb API but is not endorsed or certified by TMDb.</a>

### If you're having issues, check out the [troubleshooting guide](https://github.com/custom-cards/upcoming-media-card/blob/master/troubleshooting.md) before posting an issue or asking for help on the forums.

## Installation:

1. Install this component by copying [these files](https://github.com/custom-components/sensor.radarr_upcoming_media/tree/master/custom_components/radarr_upcoming_media) to `/custom_components/radarr_upcoming_media/`.
2. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
3. Add the code for the card to your `ui-lovelace.yaml`. 
4. **You will need to restart after installation for the component to start working.**

### Adding device
To add the **Radarr Upcoming Media** integration to your Home Assistant, use this My button:

<a href="https://my.home-assistant.io/redirect/config_flow_start?domain=radarr_upcoming_media" class="my badge" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg"></a>

<details><summary style="list-style: none"><h3><b style="cursor: pointer">Manual configuration steps</b></h3></summary>

If the above My button doesn’t work, you can also perform the following steps manually:

- Browse to your Home Assistant instance.

- Go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations/).

- In the bottom right corner, select the [Add Integration button.](https://my.home-assistant.io/redirect/config_flow_start?domain=radarr_upcoming_media)

- From the list, select **Radarr Upcoming Media**.

- Follow the instructions on screen to complete the setup.
</details>

**Do not just copy examples, please use config options above to build your own!**

### Sample for ui-lovelace.yaml:

    - type: custom:upcoming-media-card
      entity: sensor.radarr_upcoming_media
      title: Upcoming Movies
      

### Card Content Defaults

| key | default | example |
| --- | --- | --- |
| title | $title | "Night of the Living Dead" |
| line1 | $release | "In Theaters Mon, 10/31" if it's a theater release and more than a week away or "Available Monday" if it's a physical release and within a week.|
| line2 | $genres | "Action, Adventure, Comedy" |
| line3 | $rating - $runtime | "★ 9.8 - 01:30"
| line4 | $studio | "Laurel Group Inc."
| icon | mdi:arrow-down-bold | https://materialdesignicons.com/icon/arrow-down-bold
