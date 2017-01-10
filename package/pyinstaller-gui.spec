# -*- mode: python -*-

block_cipher = None


a = Analysis(['../ubitextract/gui.py'],
             pathex=['../'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ubitextract-gui',
          strip=False,
          upx=True,
          # False hides the cli window, useful ON to debug
          console=False,
          debug=False)

app = BUNDLE(exe,
             name='ubitextract-gui.app',
             bundle_identifier=None,
             info_plist={'NSHighResolutionCapable': 'True'})
