from setuptools import setup
from pathlib import Path
from subprocess import check_call
from setuptools.command.build_py import build_py
from setuptools.command.editable_wheel import editable_wheel
import zipfile
import shutil


def build_icons(target_dir):
    target_dir.mkdir(parents=True, exist_ok=True)
    rcc_file = target_dir / '_icons.rcc'
    qrc_file = Path('icons', 'icons.qrc')
    # We write a single .rcc file useable by Qt5 and Qt6. rcc format version 1 supports
    # all version of Qt5, whereas the default version 3 requires Qt 5.13+.
    options = ['--binary', '--format-version', '1']
    check_call(['pyside6-rcc', *options, '-o', str(rcc_file), str(qrc_file)])


def download_fonts(target_dir):
    import requests

    VERSION = '0.83'
    HASH = "0cef8205"
    NAME = f"ubuntu-font-family-{VERSION}"
    ZIPFILE = f"{HASH}-{NAME}.zip"
    URL = f"https://assets.ubuntu.com/v1/{ZIPFILE}"

    unzip_dir = target_dir / NAME
    dest_dir = target_dir / 'ubuntu-font-family'
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(dest_dir, ignore_errors=True)

    print('Downloading Ubuntu fonts...')
    response = requests.get(URL)
    try:
        temp_zip = Path(target_dir) / ZIPFILE
        if not response.ok:
            raise ValueError(f"{response.status_code} {response.reason}")
        temp_zip.write_bytes(response.content)
        with zipfile.ZipFile(temp_zip) as zip_ref:
            files = [f for f in zip_ref.namelist() if f.startswith(f"{NAME}/")]
            zip_ref.extractall(path=target_dir, members=files)
        # Rename to remove version number:
        unzip_dir.rename(dest_dir)
    finally:
        temp_zip.unlink(missing_ok=True)


class custom_build_py(build_py):
    def run(self):
        if not self.dry_run:
            build_icons(Path(self.build_lib) / 'qtutils' / 'icons')
            download_fonts(Path(self.build_lib) / 'qtutils' / 'fonts')
        super().run()


class custom_editable_wheel(editable_wheel):
    def run(self):
        if not self.dry_run:
            build_icons(Path('qtutils/icons'))
            download_fonts(Path('qtutils/fonts'))
        super().run()


setup(
    cmdclass={
        'build_py': custom_build_py,
        'editable_wheel': custom_editable_wheel,
    }
)
