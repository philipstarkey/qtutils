from pathlib import Path

from qtutils.qt.QtGui import QFontDatabase

FONTS_DIR = Path(__file__).parent / "ubuntu-font-family"

fonts_loaded = False

def load_fonts():
    """Add bundled fonts to the Qt Font Database"""
    global fonts_loaded
    if not fonts_loaded:
        try:
            font_files = [p for p in FONTS_DIR.iterdir() if p.suffix == '.ttf']
            if not font_files:
                raise FileNotFoundError
            for path in FONTS_DIR.iterdir():
                if path.suffix == '.ttf':
                    QFontDatabase.addApplicationFont(str(path))
        except FileNotFoundError:
            msg = (
                f"Bundled font directory {FONTS_DIR} not found or contains no fonts. "
                + "If you're running from a source directory, be sure to run "
                + "`pip install -e .` to download bundled fonts."
            )
            raise FileNotFoundError(msg) from None
    fonts_loaded = True
