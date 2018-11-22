import pathlib

class Importer:

    def __init__(self, extrapaths=None):

        self._paths = extrapaths or []
        self._paths.append(pathlib.Path('.'))

    @property
    def path(self):
        return self._paths

    def add_path(self, newpath):
        self._paths.append(newpath)

    def remove_path(self, path):
        self._paths.remove(path)

    def import_file(self, filepath):

        for path in self.path:
            try:
                return (path / filepath).with_suffix('.rdfsh').read_text()
            except FileNotFoundError:
                pass

        return None
