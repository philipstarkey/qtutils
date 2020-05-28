from pathlib import Path

here = Path(__file__).parent
icon_folders = [here / 'custom', here / 'fugue']

HEADER = """<!DOCTYPE RCC><RCC version="1.0">
  <qresource  prefix="/qtutils">"""

FOOTER = """  </qresource>
</RCC>"""

def make_qrc_file():
    lines = [HEADER]
    for folder in icon_folders:
        for filename in folder.iterdir():
            lines.append(f"    <file>{folder.name}/{filename.name}</file>")
    lines.append(FOOTER)
    Path(here, 'icons.qrc').write_text("\n".join(lines))


if __name__ == '__main__':
    make_qrc_file()