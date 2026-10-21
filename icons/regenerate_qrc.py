from pathlib import Path

here = Path(__file__).parent
icon_folders = [here / 'custom', here / 'fugue']

HEADER = """<!DOCTYPE RCC><RCC version="1.0">
  <qresource  prefix="/qtutils">"""

FOOTER = """  </qresource>
</RCC>"""

def make_qrc_file():
    """Each icon is listed under its file name and under an alias without the extension,
    so that both ':/qtutils/fugue/name.png' and ':/qtutils/fugue/name' resolve, and the
    '@2x' variant of either is found by Qt on high-DPI screens. The resource compiler
    stores a file listed twice only once."""
    lines = [HEADER]
    for folder in icon_folders:
        for filename in sorted(folder.iterdir()):
            lines.append(f"    <file>{folder.name}/{filename.name}</file>")
            lines.append(f'    <file alias="{folder.name}/{filename.stem}">{folder.name}/{filename.name}</file>')
    lines.append(FOOTER)
    Path(here, 'icons.qrc').write_text("\n".join(lines))


if __name__ == '__main__':
    make_qrc_file()