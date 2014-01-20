import pkg_resources

version_file = pkg_resources.resource_filename(__name__, 'VERSION')
with open(version_file) as vf:
    __version__ = vf.read()
del version_file


from static.apps import (
    BaseMagic,
    cling_wrap,
    Cling,
    MagicError,
    MoustacheMagic,
    Shock,
    StatusApp,
    StringMagic)


__all__ = ['__version__',
           'BaseMagic',
           'cling_wrap',
           'Cling',
           'MagicError',
           'MoustacheMagic',
           'Shock',
           'StatusApp',
           'StringMagic']
