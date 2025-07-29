"""The [preserves.error][] module exports various `Error` subclasses."""

class DecodeError(ValueError):
    """Raised whenever [preserves.binary.Decoder][] or [preserves.text.Parser][] detect invalid
    input."""
    pass

class EncodeError(ValueError):
    """Raised whenever [preserves.binary.Encoder][] or [preserves.text.Formatter][] are unable to proceed."""
    pass

class ShortPacket(DecodeError):
    """Raised whenever [preserves.binary.Decoder][] or [preserves.text.Parser][] discover that
    they want to read beyond the end of the currently-available input buffer in order to
    completely read an encoded value."""
    pass
