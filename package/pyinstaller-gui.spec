# -*- mode: python -*-
# PyInstaller additional datas and hidden import from:
# https://github.com/pyocd/pyOCD/issues/1529#issuecomment-1758960044
import os
import pathlib

from PyInstaller.utils.hooks import get_package_paths, collect_entry_point


datas_probe, hiddenimports_probe = collect_entry_point('pyocd.probe')
datas_rtos, hiddenimports_rtos = collect_entry_point('pyocd.rtos')
datas = [
    (get_package_paths('pyocd')[1], 'pyocd'),
    (get_package_paths('pylink')[1], 'pylink')
]

# Right now we exclude cmsis_pack_manager, but could be needed in the future
# datas.append((get_package_paths('cmsis_pack_manager')[1], 'cmsis_pack_manager'))
excludes = ['cmsis_pack_manager']

a = Analysis(['../ubittool/gui.py'],
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

# There isn't a way to exclude files, so remove them from collected datas.
# This removes the pyocd/target/builtin/target_xxxx.py files unless for Nordic.
# And replaces the svd_data.zip file with a slimmer version manually modified.
# Datas format: ("<package_path_to_file>", "<full_path_to_file>", 'DATA')
modified_datas = [d for d in a.datas if d[0] != 'pyocd/debug/svd/svd_data.zip' and
    not (d[0].startswith("pyocd/target/builtin/target_") and not d[0].startswith("pyocd/target/builtin/target_nRF"))]

modified_datas.append((
    'pyocd/debug/svd/svd_data.zip',
    str(pathlib.Path(os.getcwd()).resolve() / 'package' / 'svd_data.zip'),
    'DATA')
)
a.datas = tuple(modified_datas)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=None)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ubittool-gui',
          strip=False,
          upx=False,
          # False hides the cli window, useful ON to debug
          console=False,
          debug=False)

app = BUNDLE(exe,
             name='ubittool-gui.app',
             bundle_identifier=None,
             info_plist={'NSHighResolutionCapable': 'True'})

# Uncomment this for debugging purposes
# coll = COLLECT(exe,
#                a.binaries,
#                a.zipfiles,
#                a.datas,
#                strip=False,
#                upx=True,
#                upx_exclude=[],
#                name='ubittool-gui-bundle')
