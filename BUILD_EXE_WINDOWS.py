import PyInstaller.__main__
import os
APP_NAME = "Universal_Audio_Studio"
datas = [('templates', 'templates'), ('ffmpeg.exe', '.'), ('ffprobe.exe', '.')]
hidden_imports = ['sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree', 'sklearn.tree._utils', 'scipy.special.cython_special', 'scipy.spatial.transform._rotation_groups', 'librosa', 'pydub', 'engineio.async_drivers.threading', 'scipy.integrate.lsoda', 'scipy.integrate.vode', 'scipy.integrate.dop', 'scipy.integrate.dop853']
print("🚀 COMPILATION EXE...")
PyInstaller.__main__.run(['app.py', '--name=%s' % APP_NAME, '--onedir', '--noconsole', '--clean', *['--add-data=%s;%s' % (src, dst) for src, dst in datas], *['--hidden-import=%s' % mod for mod in hidden_imports], '--additional-hooks-dir=.'])
print("\n✅ TERMINE !")
