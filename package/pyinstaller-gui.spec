# -*- mode: python -*-

a = Analysis(['../ubittool/gui.py'],
             pathex=['../'],
             binaries=None,
             datas=None,
             hiddenimports=[],
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
