# Goldened-Shrines
BOTW All Shrines Community Sum-of-Best (SoB) Project

## About the Project
### Introduction
The goal of the project is to find out the fastest time humanly possible to complete an All Shrines run within real-time-attack (RTA) settings. 

Unlike Best Theoretical Time (BTT), another BOTW project similar to this that was focused on the fastest time possible using TAS-like strats, this project focuses on strats that are reproduced consistently and viable to implement in an RTA run.

### Route
The project uses the [All Shrines v3.3](https://celer.itntpiston.app/#/gh/iTNTPiston/as3) route

### Segment and Submission
This section explains how segments work and how you can submit your time to the project
#### Segments
The project uses 120 Shrine segments, 12 Warp segments, 1 Tower segment, 1 Plateau (Paraglider) segment, and 4 End Game segments (Castle, Blights, Calamity, Dark Beast). 138 segments total.

See [the reference page](docs/reference/README.md) for examples of the start/end frames. In the descriptions below, the first and last frames are inclusive.

**Timing for first segment (Ja Baij)** is from first frame of the run to first frame before cage break. When the cage breaks as you complete a shrine, it starts glowing, then the glow stops for 1 frame, then the cage starts breaking. The 1 frame where the glow stops is the last frame of this segment

**Timing for Tower segment** is from first frame of cage break (the frame after the frame where the glow stops), to the last frame where the terminal is not glowing

**Timing for magnesis segment (Oman Au)** is from first frame of an orange glow being visible on the tower terminal, to the frame of cage not glowing before breaking

**Timing for shrine-to-shrine segment** is from the first frame of cage breaking to the frame of cage not glowing before breaking

**Timing for paraglider segment** is from first frame of cage breaking, to the frame where the triangle is smaller

**Timing for paraglider-shrine segment** is from the frame after the triangle being smaller to the frame before cage break

**Timing for shrine-to-warp segment** is from first frame of cage break to the frame before the screen is completely dark after warp animation

**Timing for warp-to-shrine segment** is from first frame of screen is completely dark to the frame before cage break

**Timing for castle segment** is from first frame of cage break to last frame of windblight not exploding

**Timing for blights segment** is from first frame of windblight exploding to last frame before the screen is completely dark after thunderblight is dead

**Timing for calamity segment** is from the first frame of screen being completely dark after thunderblight is dead, to the last frame of screen not being completely white after calamity is dead

**Timing for dark beast segment** is from the first frame of screen being completely white after calamity is dead, to the last frame of dark beast's health bar is not white after firing the final shot

I have a script that will splice and time the segment submissions. **I am the single source of truth for timing** to avoid any confusion.

#### Requirement
For your segment to be considered, it must meet these requirements:

1. **Must be played on original hardware, not emulator**
2. **Must be done in a real run or in a setting similar to a real run**
    - Segments from a time-attack (TA) run is allowed if the segment doesn't pause the run
    - Reloading and grinding a segment over and over again is not allowed. This is to keep loads as consistent as possible to a real run
3. **Must be recorded at at least 30fps**
4. **Must be unspliced**
    - You cannot splice together the movement to a shrine with the movement inside a shrine, for example, even if both are done in a real run
5. **Must have game audio**
6. **Must be consistent with the route**
    - List of inconsistencies allowed (exhaustive): 
      - Different things equipped (including runes and armor)
      - Different effect timer or didn't/did eat potion/food
      - Skipping cutting trees because of good rng
      - Different time of day
      - Different health/max health
      - Different stamina only allowed if you do not use more than 7/5 stamina wheels at any given time in your segment
      - Getting unloaded shrine
    - Examples of inconsistencies not allowed:
      - Not getting shield of minds eye in Taloh Naeg segment
      - Getting medoh cutscene before entering Akh Vaquot and therefore have a faster Bareeda Naeg segment
      - Skipping setting time of day because it happened to be the right time of day during the run for some reason
7. **Must not scan amiibo or use the amiibo prompt at a shrine not specified by the route**
    - Using amiibo prompt to activate SCW is allowed for Joloo Nah only, to avoid complications. However, if there is a combination of segments that result in a significantly faster time and only used amiibo prompt once, for another shrine, it will be considered

Additionally, it's preferable if the segment also meets the following:

1. Recorded at 1080p. Lower resolutions are allowed, but your segment may be rejected if the quality is too low
2. Recorded at exactly 30fps. Higher fps will be converted or re-encoded to 30fps beforing timing, which may result in inaccurate time but that's the best we can do
3. Recorded using a capture device. If it's recorded with a camera over the console screen, it may be rejected if the recording quality is too low
4. Played on switch. Wii U is allowed if there's no major inconsistencies between switch and Wii U for that segment
5. Have clean gameplay audio only. This is a very minor factor and your segment will not be rejected solely because you have another audio source. However, it is recommended to setup a track in your recording software that only captures game audio, so it can be separated from the other audio sources

Needless to say, your segment also needs to be at least as fast as the current segment. In case of a tie, the one with better movement will be chosen, or you can convince me to use yours instead of the existing one.

By submitting a segment, you also automatically agree to let me store your segment locally and on Google Cloud and/or YouTube, and include parts or all of your submission in the final video

#### Workflow
This is how this project works

Submission:
1. People submit video containing the segment to me
2. I look at the video, extract the segment from the video and re-encoding it if needed
3. I time the segment, reject if slower than existing
4. If accepted, I make sure the audio level is good when mixed with other segments
5. I upload the segment to Google Cloud and include the segment information in the project
6. I run a script to update the timing info for the project

Every so often, I will press a button that automatically renders the full video with splits. And upload that to youtube or find someone to premier it

## Environment Setup
This section and below are for people who wants to render the project
### Recommended Hardware
Building this project is very intensive on the hardware. A CPU with 8 or 16 cores is recommended. Dedicated GPU is strongly recommended. The scripts use nvidia settings, so if you have an AMD card, you might need to tweak some ffmpeg settings yourself.

### Install Tools

#### Python
Python 3 is needed. Install these modules
```
python3 -m pip install toml
```

#### yt-dlp 
A tool to download videos. https://github.com/yt-dlp/yt-dlp

make sure `yt-dlp` is in `PATH`

#### ffmpeg
A tool to process videos. https://ffmpeg.org/download.html

make sure `ffmpeg.exe`, `ffplay.exe` and `ffprobe.exe` is are `PATH`



need log output, html generation, and head/tail video editing
