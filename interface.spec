# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['interface.py'],
             pathex=[],
             binaries=[],
             datas=[
                ('C:\\sbis\\cropio\\def_simple.xlsx', 'def'),
                ('C:\\sbis\\cropio\\def_kamaz.xlsx', 'def'),
                ('C:\\sbis\\cropio\\def_production.xlsx', 'def')
            ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='interface',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
