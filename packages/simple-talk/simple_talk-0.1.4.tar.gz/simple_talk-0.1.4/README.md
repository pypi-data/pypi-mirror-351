# Introduction

This library provides simple Pythonic interface to use specified text-to-speech synthesizer.

It supports following synthesizers:

- macOS's builtin synthesizer
  - Only allows personal, non-commercial use (as stated in macOS software license agreement).
  - Outputs mp4 file.
- eSpeak NG
  - Requires installing eSpeak NG CLI first.
  - Outputs wav file.
- Amazon Polly
  - Requires installing with extra `simple-talk[polly]`
  - Must specify [engine and voice](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly/client/synthesize_speech.html)
  - Outputs mp3 file.

# How to Install

It is available on PyPI under name [`simple-talk`](https://pypi.org/project/simple-talk/).

# How to Use

It is straight-forward as below:

``` python
In [1]: from simple_talk import SimpleTalk

In [2]: s = SimpleTalk()

In [3]: s.talk("Hello world!", "output")
```

In addition, you can specify voice and/or synthesizer when constructing `SimpleTalk` object.

You can specify output filename without suffix, and it will return you full output filename with respective suffix.
Otherwise, if output filename is not specified, an object of class [`AudioFileClip`](https://zulko.github.io/moviepy/reference/reference/moviepy.audio.io.AudioFileClip.AudioFileClip.html#moviepy.audio.io.AudioFileClip.AudioFileClip) from `MoviePy` is returned, and you can further use it to write to any audio file with any `MoviePy` supported audio format.

``` python
...

In [3]: clip = s.talk("Hello world!")

In [4]: clip.write_audiofile("output.mp3")
```
