# -*- mode: python -*-
from sys import version_info


if version_info.major == 3:
    excludes = ['tkinter']
elif version_info.major == 2:
    excludes = ['Tkinter', 'tkMessageBox', 'tkFileDialog']


a = Analysis(['../ubittool/cli.py'],
             pathex=['../'],
             binaries=None,
             datas=None,
             hiddenimports=[],
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
