# Regression tests

The suite covers MIDI parsing, NLA copying, Dope Sheet copying, Graph Editor keyframe generation, instruments, filters, presets, file loading, `load_post`, registration, and translations. Parser tests assert note times and event values. Blender tests assert strip frames, keyframe values, and reported errors.

## Run against a Blender build

```bash
python tests/run_tests.py /path/to/blender
```

`/path/to/blender` is the Blender executable. The runner launches it as:

```bash
blender -b --factory-startup --python tests/run_tests.py
```

It installs this checkout as a user extension, then prints `PASS`, `FAIL`, or `SKIP` for every test. The process exits with status 1 if any test fails.

Write a machine-readable summary, or resume the Blender tests at one name:

```bash
python tests/run_tests.py /path/to/blender --results /tmp/nla-midi-results.json
python tests/run_tests.py /path/to/blender --from-test test_load_post
```

Official builds and daily alphas from [builder.blender.org](https://builder.blender.org/download/daily/) both work. Point the command at `blender` inside the unpacked directory, for example:

```bash
python tests/run_tests.py ~/blender/blender-4.2.23-stable+v42-linux.x86_64-release/blender
python tests/run_tests.py ~/blender/blender-4.5.15-stable+v45-linux.x86_64-release/blender
python tests/run_tests.py ~/blender/blender-5.2.3-stable+v52-linux.x86_64-release/blender
python tests/run_tests.py ~/blender/blender-5.4.0-alpha+main-linux.x86_64-release/blender
```

The add-on's manifest allows Blender 4.2 and newer and does not set a maximum version.

## Parser tests without Blender

```bash
python -m unittest tests.test_midi_parser
```

These import `midi_analysis` directly. The Blender runner executes them too, so one command covers the whole suite.

MIDI files are generated in a temporary directory by `tests/midi_builder.py`. `tests/fixtures/piano_format1.mid` is a small committed format 1 file used by the parser tests.
