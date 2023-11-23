# -*- mode: python -*-
# PyInstaller additional datas and hidden import from:
# https://github.com/pyocd/pyOCD/issues/1529#issuecomment-1758960044
from PyInstaller.utils.hooks import get_package_paths, collect_entry_point

datas_probe, hiddenimports_probe = collect_entry_point('pyocd.probe')
datas_rtos, hiddenimports_rtos = collect_entry_point('pyocd.rtos')

datas = [
    (get_package_paths('pyocd')[1], 'pyocd'),
    (get_package_paths('cmsis_pack_manager')[1], 'cmsis_pack_manager'),
    (get_package_paths('pylink')[1], 'pylink')
]


a = Analysis(['../ubittool/gui.py'],
             pathex=['../'],
             binaries=None,
             datas=datas + datas_probe + datas_rtos,
             hiddenimports=hiddenimports_probe + hiddenimports_rtos,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
