# -*- mode: python -*-
a = Analysis(['spider/spider.py'],
             pathex=['J:\\pyinstaller-2.0'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'spider.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
