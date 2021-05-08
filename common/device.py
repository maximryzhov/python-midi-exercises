import logging
import time

import rtmidi

# MIDI messages reference: https://www.midi.org/specifications-old/item/table-2-expanded-messages-list-status-bytes
# MIDI control messages reference: https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2

logger = logging.getLogger(__name__)

GM_INSTRUMENTS = [
    'Acoustic Grand Piano', 'Bright Acoustic Piano', 'Electric Grand Piano',
    'Honky-tonk Piano', 'Electric Piano 1', 'Electric Piano 2', 'Harpsichord',
    'Clavinet', 'Celesta', 'Glockenspiel', 'Music Box', 'Vibraphone',
    'Marimba', 'Xylophone', 'Tubular Bells', 'Dulcimer', 'Drawbar Organ',
    'Percussive Organ', 'Rock Organ', 'Church Organ', 'Reed Organ',
    'Accordion', 'Harmonica', 'Tango Accordion', 'Acoustic Guitar (nylon)',
    'Acoustic Guitar (steel)', 'Electric Guitar (jazz)',
    'Electric Guitar (clean)', 'Electric Guitar (muted)', 'Overdriven Guitar',
    'Distortion Guitar', 'Guitar harmonics', 'Acoustic Bass',
    'Electric Bass (finger)', 'Electric Bass (pick)', 'Fretless Bass',
    'Slap Bass 1', 'Slap Bass 2', 'Synth Bass 1', 'Synth Bass 2', 'Violin',
    'Viola', 'Cello', 'Contrabass', 'Tremolo Strings', 'Pizzicato Strings',
    'Orchestral Harp', 'Timpani', 'String Ensemble 1', 'String Ensemble 2',
    'Synth Strings 1', 'Synth Strings 2', 'Choir Aahs', 'Voice Oohs',
    'Synth Voice', 'Orchestra Hit', 'Trumpet', 'Trombone', 'Tuba',
    'Muted Trumpet', 'French Horn', 'Brass Section', 'Synth Brass 1',
    'Synth Brass 2', 'Soprano Sax', 'Alto Sax', 'Tenor Sax', 'Baritone Sax',
    'Oboe', 'English Horn', 'Bassoon', 'Clarinet', 'Piccolo', 'Flute',
    'Recorder', 'Pan Flute', 'Blown Bottle', 'Shakuhachi', 'Whistle',
    'Ocarina', 'Lead 1 (square)', 'Lead 2 (sawtooth)', 'Lead 3 (calliope)',
    'Lead 4 (chiff)', 'Lead 5 (charang)', 'Lead 6 (voice)', 'Lead 7 (fifths)',
    'Lead 8 (bass + lead)', 'Pad 1 (new age)', 'Pad 2 (warm)',
    'Pad 3 (polysynth)', 'Pad 4 (choir)', 'Pad 5 (bowed)', 'Pad 6 (metallic)',
    'Pad 7 (halo)', 'Pad 8 (sweep)', 'FX 1 (rain)', 'FX 2 (soundtrack)',
    'FX 3 (crystal)', 'FX 4 (atmosphere)', 'FX 5 (brightness)',
    'FX 6 (goblins)', 'FX 7 (echoes)', 'FX 8 (sci-fi)', 'Sitar', 'Banjo',
    'Shamisen', 'Koto', 'Kalimba', 'Bag pipe', 'Fiddle', 'Shanai',
    'Tinkle Bell', 'Agogo', 'Steel Drums', 'Woodblock', 'Taiko Drum',
    'Melodic Tom', 'Synth Drum', 'Reverse Cymbal', 'Guitar Fret Noise',
    'Breath Noise', 'Seashore', 'Bird Tweet', 'Telephone Ring', 'Helicopter',
    'Applause', 'Gunshot'
]

class Device:
    """
    Class that represents a single MIDI Out device
    """
    def __init__(self, port=0):
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_port(port)
        available_ports = self.midi_out.get_ports()
        logger.info(f"Opened port: {available_ports[port]}")

    def quit(self):
        self.midi_out.close_port()
        del self.midi_out

    def set_instrument(self, channel, instrument, msb=0, lsb=0):
        # Set bank MSB
        self.midi_out.send_message([176 + channel, 0, msb])
        # Set bank LSB
        self.midi_out.send_message([176 + channel, 32, lsb])
        # Set patch number
        self.midi_out.send_message([192 + channel, instrument, 0])

        # Currently displays correct instrument names only for General MIDI Level 1 sound set
        # https://www.midi.org/specifications-old/item/gm-level-1-sound-set
        logger.info(f"Channel {channel + 1} instrument set: {GM_INSTRUMENTS[instrument]}")

    def note_on(self, channel, note, velocity=127):
        self.midi_out.send_message([144 + channel, note, velocity])

    def note_off(self, channel, note, velocity=127):
        self.midi_out.send_message([128 + channel, note, velocity])

    def all_notes_off(self):
        for ch in range(0, 16):
            self.midi_out.send_message([176 + ch, 123, 0])

    def test_channel(self, channel):
        """
        Plays a C5 note on selected MIDI channel for 1 second
        """
        note = 60 # C5
        self.note_on(channel, note)
        time.sleep(1)
        self.note_off(channel, note)