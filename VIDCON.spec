# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['VIDCON.py'],
             pathex=['C:\\Users\\DELL\\PLAYGROUND\\hkdevstudio\\VIDCON'],
             binaries=[('C:\\Users\\DELL\\PLAYGROUND\\Anaconda3\\Lib\\site-packages\\cv2\\opencv_videoio_ffmpeg420_64.dll','.')],
             datas=[],
             hiddenimports=[('pkg_resources.py2_warn')],
             hookspath=[],
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
          name='VIDCON',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
