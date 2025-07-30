# Geekar

Geekar is a guitar learning application for the Linux terminal.


## Features

It features an interactive fretboard that displays:

- Major and natural minor scales
- Major and minor pentatonic scales
- Scale notes and degrees
- Triads for each scale degree

![](screenshots/geekar-start.png)

Geekar facilitates study of the CAGED system. For each supported scale it colors the fretboard accordingly.

![](screenshots/geekar-c-major-caged.png)

The interactive fretboard is playable. Click on a fretboard location and listen to the corresponding pitch.

![](screenshots/geekar-c-major-pitch-play.png)

Supported scales can also be played. Geekar suggests the finger that should be used.

![](screenshots/geekar-c-major-play-scale.png)

A very simple metronome has also been included in the application.

## Build

Geekar has been written using the [textualize](https://textual.textualize.io/) framework.

It has the following system dependencies:

- fluidsynth

To build the application, execute on a Python virtual environment:

```
pip install -e ".[dev]"
```

## License

Geekar has been created by human beings for human beings. It is a free and open source project licensed under AGPL v3 only.
If you find its code as training input for [non-foss ML models](https://sfconservancy.org/blog/2024/oct/31/open-source-ai-definition-osaid-erodes-foss/) consider it stolen.

