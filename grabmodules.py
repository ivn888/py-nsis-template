import importlib, importlib.abc
import os
import shutil
import sys
import zipfile, zipimport

class ModuleCopier:
    def __init__(self, path=None):
        self.path = path if (path is not None) else sys.path
    
    def copy(self, modname, target):
        loader = importlib.find_loader(modname, self.path)
        pkg = loader.is_package(modname)
        file = loader.get_filename(modname)
        if isinstance(loader, importlib.abc.FileLoader):
            if pkg:
                pkgdir, basename = os.path.split(file)
                assert basename.startswith('__init__')
                dest = os.path.join(target, modname)
                shutil.copytree(pkgdir, dest, ignore=shutil.ignore_patterns('*.pyc'))
            else:                
                shutil.copy2(file, target)
        
        elif isinstance(loader, zipimport.zipimporter):
            prefix = loader.archive + '/' + loader.prefix
            assert file.startswith(prefix)
            path_in_zip = file[len(prefix):]
            zf = zipfile.ZipFile(loader.archive)
            if pkg:
                pkgdir, basename = path_in_zip.rsplit('/', 1)
                assert basename.startswith('__init__')
                pkgfiles = [f for f in zf.namelist() if f.startswith(pkgdir)]
                zf.extractall(target, pkgfiles)
            else:
                zf.extract(path_in_zip, target)