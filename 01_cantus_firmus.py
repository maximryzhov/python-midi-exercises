"""
Based on http://openmusictheory.com/cantusFirmus.html

Rules:
1. length of about 8–16 notes
2. arhythmic (all whole notes; no long or short notes)
3. begin and end on do
4. approach final tonic by step (usually re–do, sometimes ti–do)
5. all note-to-note progressions are melodic consonances
6. range (interval between lowest and highest notes) of no more than a tenth, usually less than an octave
7. a single climax (high point) that appears only once in the melody
8. clear logical connection and smooth shape from beginning to climax to ending
9. mostly stepwise motion, but with some leaps (mostly small leaps)
10. no repetition of “motives” or “licks”
11. any large leaps (fourth or larger) are followed by step in opposite direction
12. no more than two leaps in a row; no consecutive leaps in the same direction
(Fux’s F-major cantus is an exception, where the back-to-back descending leaps outline a consonant triad.)
13. the leading tone progresses to the tonic
14. in minor, the leading tone only appears in the penultimate bar; the raised submediant is only used when progressing to that leading tone
"""

import time
import random
import argparse

from common.scales import MAJOR_SCALE, MINOR_SCALE
from common.device import Device


class CantusFirmus:
    """
    Cantus firmus generator using (mostly) brute force algorithm:
    1. Create a sequence of notes
    2. If the sequence doesn't match the rules go to 1
    """

    # Range between the lowest and the highest note (Rule 6)
    MAX_RANGE = 7

    # Number of retries after which the set of rules
    # is considered impossible
    MAX_CYCLES = 100_000

    def __init__(self):
        self._length: int = None
        self._scale: tuple[int] = None
        self._degrees: list = []

        self._intervals = []
        self._directions = []
        self._cycles = 0

    def _choose_direction(self, current_note_index):
        # If the previous interval is a fourth or larger,
        # go in the opposite direction (Rule 11)
        if current_note_index > 1 and abs(self._intervals[current_note_index-1]) > 2:
            return self._directions[current_note_index-1] * -1
        else:
            return random.choice((1, -1))

    def _choose_interval(self, current_note_index):
        # If two previous intervals are a P4 or larger
        # choose from M2/m2 or M3/m3 (Rule 12:  no more than two leaps in a row)
        if current_note_index > 1 and abs(self._intervals[current_note_index-1]) > 2\
        and abs(self._intervals[current_note_index-2]) > 2:
            intervals = (1, 2)

        # Chose from M2/m2, M3/m3 and P4 intervals (Rule 5 and 9)
        else:
            intervals = (1, 2, 3)
        return random.choice(intervals)

    def _make_next_note(self, current_note_index):
        interval = self._choose_interval(current_note_index)
        direction = self._choose_direction(current_note_index)
        interval *= direction

        previous_note = self._degrees[current_note_index-1]
        note = previous_note + interval
        self._degrees.append(note)

        # Store interval and direction for the next iteration
        self._intervals.append(interval)
        self._directions.append(direction)

        return note

    def _check_rules(self):
        if not self._check_rule_3():
            return False
        if not self._check_rule_4():
            return False
        if not self._check_rule_6():
            return False
        if not self._check_rule_7():
            return False
        if not self._check_rule_8():
            return False
        if not self._check_rule_10():
            return False
        if not self._check_rule_13():
            return False
        return True

    def _check_rule_3(self):
        """
        Sequence should end on the tonic
        """
        return self._degrees[-1] == 0

    def _check_rule_4(self):
        """
        Sequence should approach the final tonic from the second or seventh note of the scale
        """
        return self._degrees[-2] in (1, -1, 6, -6)

    def _check_rule_6(self):
        """
        The range between the lowest and the highest note should be less than an octave
        """
        lowest_note = min(self._degrees)
        highest_note = max(self._degrees)
        if abs(highest_note - lowest_note) > self.MAX_RANGE:
            return False
        return True

    def _check_rule_7(self):
        """
        A single climax (high point) that appears only once in the melody
        """
        highest_note = max(self._degrees)
        if self._degrees.count(highest_note) > 1:
            return False

        # Highest note should be in the middle or further
        if self._degrees.index(highest_note) < self._length // 2:
            return False

        # Highest note should be at least on the 3rd step
        if highest_note < 3:
            return False
        return True

    def _check_rule_8(self):
        """
        clear logical connection and smooth shape from beginning to climax to ending
        """
        # Let's define "smooth shape and logical connection"
        # as "3 consecutive steps up or down"
        num_steps = 3
        up_slope = [1] * num_steps
        down_slope = [-1] * num_steps

        up_slopes_count = 0
        down_slopes_count = 0

        for i in range(0, len(self._degrees) - num_steps):
            if self._directions[i:i + num_steps] == up_slope:
                up_slopes_count += 1
            elif self._directions[i:i + num_steps] == down_slope:
                down_slopes_count += 1

        return up_slopes_count > 0 or down_slopes_count > 0

    def _check_rule_10(self):
        """
        no repetition of “motives” or “licks”
        """
        # Let's define a "motive" as a sequence of 2 notes
        motive_length = 2

        # Get all possible motives
        motives = []
        for i in range(0, self._length - motive_length + 1):
            motive = self._degrees[i:i + motive_length]
            motives.append(motive)

        # Count occurences of each motive
        for entry in motives:
            if motives.count(entry) > 1:
                return False

        return True

    def _check_rule_13(self):
        """
        the leading tone progresses to the tonic
        """
        # Sixth degree is a leading tone in natural major scale
        if self._scale == MAJOR_SCALE:
            for i in range(0, self._length - 1):
                if self._degrees[i] == -1 and self._degrees[i + 1] != 0:
                    return False
                if self._degrees[i] == 6 and self._degrees[i + 1] != 7:
                    return False
        return True

    def make_notes(self, length, scale):
        # Rule 1
        if length < 8 or length > 16:
            raise Exception("length should be between 8 and 16")

        self._length = length
        self._scale = scale

        # Generate notes and store them
        # as degrees of the diationic scale
        success = False
        self._cycles = 0
        while success is False:

            if self._cycles > self.MAX_CYCLES:
                raise Exception(
                    "Sequence takes too long to generate or the current set of rules is impossible to match"
                )

            # Sequence should start with the tonic (Rule 3)
            self._degrees = [0,]
            # Reset variables
            self._intervals = [0, ]
            self._directions = [0, ]

            current_note = 0

            for i in range(1, self._length):
                current_note = self._make_next_note(i)
            success = self._check_rules()
            self._cycles += 1

        print(f"Generated in {self._cycles} cycles")

    def get_notes(self, base_note=60):
        # First, wrap scale degrees around and transpose by an octave.
        # Since the range of cantus firmus shouldn't exceed 1 octave
        # we check only 1 octave up and down.
        # Then convert scale degree to MIDI note number

        if len(self._degrees) == 0:
            raise Exception("You should call 'make_notes' method first")

        result = []
        for degree in self._degrees:
            if degree > 6:
                note = base_note + self._scale[degree - 7] + 12
            elif degree >= 0:
                note = base_note + self._scale[degree]
            else:
                note = base_note + self._scale[7 + degree] - 12
            result.append(note)
        return result


def note_to_letter(note):
    """
    Convert MIDI pitch value to a readable note
    """
    octave = note // 12
    letter = {
        0: 'C',
        1: 'C#',
        2: 'D',
        3: 'D#',
        4: 'E',
        5: 'F',
        6: 'F#',
        7: 'G',
        8: 'G#',
        9: 'A',
        10: 'A#',
        11: 'B',
    }.get(note % 12, "?")

    return f"{letter}{octave}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l",
                        "--length",
                        help="Number of notes in the melody",
                        type=int,
                        default=9)
    parser.add_argument("-b",
                        "--base_note",
                        help="MIDI pitch value",
                        type=int,
                        default=60)

    scale_group = parser.add_mutually_exclusive_group()
    scale_group.add_argument("--major", action="store_true", default=True)
    scale_group.add_argument("--minor", action="store_true")

    args = parser.parse_args()

    if args.major:
        scale = MAJOR_SCALE
    if args.minor:
        scale = MINOR_SCALE

    cf = CantusFirmus()
    cf.make_notes(args.length, scale)
    midi_notes = cf.get_notes(base_note=args.base_note)

    d = Device(0)
    d.set_instrument(0, 52)  # Switch to "Choir Aahs" instrument
    for n in midi_notes:
        print(note_to_letter(n), end=" ", flush=True)
        d.note_on(0, n)
        time.sleep(1.0)
        d.note_off(0, n)
    print("\n")
