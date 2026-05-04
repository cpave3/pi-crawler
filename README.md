# picrawler-server

HTTP control surface for an LLM agent driving a SunFounder PiCrawler quadruped.

## Install (on the Pi)

```bash
pip install -e '.[pi]'
```

The `pi` extra pulls in `picrawler`, `robot-hat`, and `vilib`, which only build
on the device. For development on a workstation, install without the extra and
set `PICRAWLER_MOCK=1` to use mock hardware:

```bash
pip install -e '.[dev]'
PICRAWLER_MOCK=1 picrawler-server
```

## Run

The robot hat needs root for GPIO/I²C, so the server is launched under `sudo`
with the project's `.env` file exported into the environment:

```bash
sudo -E env $(cat .env | xargs) picrawler-server
```

`.env` should set at least:

```
PICRAWLER_TOKEN=<bearer token clients must send>
PICRAWLER_PORT=8000          # optional, defaults to 8000
PIPER_URL=http://host:port   # optional, for TTS
PIPER_VOICE=<voice name>     # optional
PICRAWLER_MIC_DEVICE=plughw:1,0   # optional, ALSA capture device for /listen
```

The Pi's default ALSA device is usually `dmix` (playback-only), so `/listen`
needs an explicit capture device. Find yours with `arecord -l` and set
`PICRAWLER_MIC_DEVICE` accordingly (or pass `device` in the request body).

The MJPEG camera stream is served on port `9000` at `/mjpg` once the server
starts.

## Tests

```bash
pytest
```

Tests run against `MockCrawler` / `MockCamera`, so they work off-device.
