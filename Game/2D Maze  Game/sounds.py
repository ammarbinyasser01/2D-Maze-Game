import pygame
import struct
import math
import io
import os

collision_sound = None
victory_sound   = None


def _make_wav(freq, ms, volume=0.6, wave="sine"):
    rate = 44100
    n = int(rate * ms / 1000)
    samples = []
    for i in range(n):
        t = i / rate
        # fade out last 20%
        fade = 1.0 - max(0, (i - n * 0.8) / (n * 0.2))
        if wave == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif wave == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == "sweep":
            f = freq * (1 + t * 3)
            v = math.sin(2 * math.pi * f * t)
        else:
            v = math.sin(2 * math.pi * freq * t)
        samples.append(int(v * fade * volume * 32767))

    raw  = struct.pack(f"<{n}h", *samples)
    size = len(raw)
    hdr  = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + size, b"WAVE",
        b"fmt ", 16, 1, 1,
        rate, rate * 2, 2, 16,
        b"data", size,
    )
    # Keep BytesIO alive by storing on the Sound object below
    buf = io.BytesIO(hdr + raw)
    snd = pygame.mixer.Sound(buf)
    snd._buf = buf   # prevent garbage collection
    return snd


def load_sounds():
    global collision_sound, victory_sound

    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        except Exception as e:
            print(f"[sounds] mixer init failed: {e}")
            return

    # collision — try file first, fall back to generated
    path = os.path.join("assets", "collision.wav")
    if os.path.exists(path):
        try:
            collision_sound = pygame.mixer.Sound(path)
            print("[sounds] loaded collision.wav")
        except Exception as e:
            print(f"[sounds] collision.wav failed: {e}")

    if collision_sound is None:
        collision_sound = _make_wav(180, 120, volume=0.7, wave="square")
        print("[sounds] using generated collision sound")

    # victory — try file first, fall back to generated
    path = os.path.join("assets", "victory.wav")
    if os.path.exists(path):
        try:
            victory_sound = pygame.mixer.Sound(path)
            print("[sounds] loaded victory.wav")
        except Exception as e:
            print(f"[sounds] victory.wav failed: {e}")

    if victory_sound is None:
        victory_sound = _make_wav(400, 700, volume=0.6, wave="sweep")
        print("[sounds] using generated victory sound")

    print(f"[sounds] ready — collision={collision_sound}, victory={victory_sound}")