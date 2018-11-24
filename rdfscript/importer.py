import pathlib

class Importer:

    def __init__(self, paths):

        self._dirs = [pathlib.Path(path).expanduser().resolve() for path in paths]
        self._dirs.append(pathlib.Path('.').resolve())

    @property
    def path(self):
        return self._dirs

    def add_path(self, newpath):
        self._dirs.append(pathlib.Path(newpath).expanduser().resolve())

    def remove_path(self, path):
        self._dirs.remove(pathlib.Path(path).resolve())

    def import_file(self, filepath):

        for dir in self._dirs:
            try:
                return (dir / filepath).with_suffix('.rdfsh').read_text()
            except FileNotFoundError:
                pass

        return None
