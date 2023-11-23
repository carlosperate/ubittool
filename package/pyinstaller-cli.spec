# -*- mode: python -*-
# -*- mode: python -*-
# PyInstaller additional datas and hidden import from:
# https://github.com/pyocd/pyOCD/issues/1529#issuecomment-1758960044
from sys import version_info

from PyInstaller.utils.hooks import get_package_paths, collect_entry_point

datas_probe, hiddenimports_probe = collect_entry_point('pyocd.probe')
datas_rtos, hiddenimports_rtos = collect_entry_point('pyocd.rtos')

datas = [
    (get_package_paths('pyocd')[1], 'pyocd'),
    (get_package_paths('cmsis_pack_manager')[1], 'cmsis_pack_manager'),
    (get_package_paths('pylink')[1], 'pylink')
]

if version_info.major == 3:
    excludes = ['tkinter']


a = Analysis(['../ubittool/cli.py'],
             pathex=['../'],
             binaries=None,
             datas=datas + datas_probe + datas_rtos,
             hiddenimports=hiddenimports_probe + hiddenimports_rtos,
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=None)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ubittool-cli',
          strip=False,
          upx=False,
          # False hides the cli window, useful ON to debug
          console=True,
          debug=False)
