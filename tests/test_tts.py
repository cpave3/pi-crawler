"""Unit tests for the WAV header parser and TTS request building."""

from picrawler_server.tts import _build_request_kwargs, parse_wav_header


def _make_wav(sample_rate: int = 44100, channels: int = 1, bits: int = 16, data_size: int = 100):
    """Build a minimal valid WAV header + some dummy PCM data."""
    import struct
    byte_rate = sample_rate * channels * bits // 8
    block_align = channels * bits // 8
    fmt_chunk = struct.pack("<4sIHHIIHH",
        b"fmt ", 16, 1, channels, sample_rate, byte_rate, block_align, bits)
    data_chunk = b"data" + struct.pack("<I", data_size) + (b"\x00" * data_size)
    riff_size = 4 + len(fmt_chunk) + len(data_chunk)
    return b"RIFF" + struct.pack("<I", riff_size) + b"WAVE" + fmt_chunk + data_chunk


def test_parse_valid_wav():
    wav = _make_wav(sample_rate=22050, channels=1, bits=16)
    result = parse_wav_header(wav)
    assert result is not None
    assert result["sample_rate"] == 22050
    assert result["channels"] == 1
    assert result["bits_per_sample"] == 16
    assert result["bytes_per_second"] == 22050 * 1 * 2


def test_parse_stereo_wav():
    wav = _make_wav(sample_rate=44100, channels=2, bits=16)
    result = parse_wav_header(wav)
    assert result is not None
    assert result["channels"] == 2
    assert result["bytes_per_second"] == 44100 * 2 * 2


def test_parse_incomplete_header():
    assert parse_wav_header(b"RIFF") is None
    assert parse_wav_header(b"") is None
    assert parse_wav_header(b"RIFF\x00\x00\x00\x00WAVE") is None


def test_parse_not_wav():
    not_wav = b"NOT_A_WAV_FILE" + b"\x00" * 44
    assert parse_wav_header(not_wav) is None


def test_build_request_kwargs_json(monkeypatch):
    monkeypatch.setattr("picrawler_server.tts.PIPER_MODE", "json")
    monkeypatch.setattr("picrawler_server.tts.PIPER_VOICE", "en_US-ryan-high")
    ok, kwargs = _build_request_kwargs("hello")
    assert ok is True
    assert kwargs["json"] == {"text": "hello", "voice": "en_US-ryan-high"}


def test_build_request_kwargs_form(monkeypatch):
    monkeypatch.setattr("picrawler_server.tts.PIPER_MODE", "form")
    ok, kwargs = _build_request_kwargs("hello")
    assert ok is True
    assert kwargs["data"] == {"text": "hello"}


def test_build_request_kwargs_raw(monkeypatch):
    monkeypatch.setattr("picrawler_server.tts.PIPER_MODE", "raw")
    ok, kwargs = _build_request_kwargs("hello")
    assert ok is True
    assert kwargs["content"] == b"hello"


def test_build_request_kwargs_unknown_mode(monkeypatch):
    monkeypatch.setattr("picrawler_server.tts.PIPER_MODE", "banana")
    ok, err = _build_request_kwargs("hello")
    assert ok is False
    assert "banana" in err
