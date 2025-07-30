#!/usr/bin/env python

# ...

from distutils.core import setup
import shutil,os

root = __file__[:__file__.rfind('/')]
lib = os.environ['HOME']+'/lib'

long_description="""
The tkinter package (“Tk interface”) is the standard Python interface to the Tcl/Tk GUI toolkit. Both Tk and tkinter are available on most Unix platforms, including macOS, as well as on Windows systems.
"""

sos = ["libXft.so", "libfontconfig.so", "libX11.so", "libXrender.so", "libtcl8.6.so", "libXext.so", "libXss.so", "libtk8.6.so", "libfreetype.so", "libxcb.so", "libpng16.so", "libbrotlidec.so", "libXau.so", "libXdmcp.so", "libbrotlicommon.so"]

setup(name='tkinter-qpython',
      version='8.6.0.5',
      description='tkinter — Python interface to Tcl/Tk',
      author='The QPYPI Team',
      author_email='qpypi@qpython.org',
      url='https://qpypi.qpython.org/project/tkinter-qpython/',
      data_files=[(lib, sos+['_tkinter.cpython-312.so'])],
      py_modules=['turtle'],
      packages=["tkinter", "idlelib", "tcl86", "tk86", "idlelib", "etc"],
      package_data={
            "idlelib":[
"CREDITS.txt",
"ChangeLog",
"HISTORY.txt",
"Icons/*",
"NEWS2x.txt",
"News3.txt",
"README.txt",
"TODO.txt",
"__init__.py",
"__main__.py",
"autocomplete.py",
"autocomplete_w.py",
"autoexpand.py",
"browser.py",
"calltip.py",
"calltip_w.py",
"codecontext.py",
"colorizer.py",
"config-extensions.def",
"config-highlight.def",
"config-keys.def",
"config-main.def",
"config.py",
"config_key.py",
"configdialog.py",
"debugger.py",
"debugger_r.py",
"debugobj.py",
"debugobj_r.py",
"delegator.py",
"dynoption.py",
"editor.py",
"extend.txt",
"filelist.py",
"format.py",
"grep.py",
"help.html",
"help.py",
"help_about.py",
"history.py",
"hyperparser.py",
"idle.bat",
"idle.py",
"idle.pyw",
"idle_test/*",
"iomenu.py",
"macosx.py",
"mainmenu.py",
"multicall.py",
"outwin.py",
"parenmatch.py",
"pathbrowser.py",
"percolator.py",
"pyparse.py",
"pyshell.py",
"query.py",
"redirector.py",
"replace.py",
"rpc.py",
"run.py",
"runscript.py",
"scrolledlist.py",
"search.py",
"searchbase.py",
"searchengine.py",
"sidebar.py",
"squeezer.py",
"stackviewer.py",
"statusbar.py",
"textview.py",
"tooltip.py",
"tree.py",
"undo.py",
"util.py",
"window.py",
"zoomheight.py",
"zzdummy.py",
],
            "etc":[
"fonts/*",
"fonts/conf.d/*",
],
            "tcl86":[
"auto.tcl",
"clock.tcl",
"encoding/*",
"history.tcl",
"http1.0/*",
"init.tcl",
"msgs/*",
"opt0.4/*",
"package.tcl",
"parray.tcl",
"safe.tcl",
"tclAppInit.c",
"tclIndex",
"tm.tcl",
"word.tcl",
],
            "tk86":[
"bgerror.tcl",
"button.tcl",
"choosedir.tcl",
"clrpick.tcl",
"comdlg.tcl",
"console.tcl",
"demos/*",
"demos/images/*",
"dialog.tcl",
"entry.tcl",
"focus.tcl",
"fontchooser.tcl",
"iconlist.tcl",
"icons.tcl",
"images/*",
"listbox.tcl",
"megawidget.tcl",
"menu.tcl",
"mkpsenc.tcl",
"msgbox.tcl",
"msgs/*",
"obsolete.tcl",
"optMenu.tcl",
"palette.tcl",
"panedwindow.tcl",
"pkgIndex.tcl",
"safetk.tcl",
"scale.tcl",
"scrlbar.tcl",
"spinbox.tcl",
"tclIndex",
"tearoff.tcl",
"text.tcl",
"tk.tcl",
"tkAppInit.c",
"tkfbox.tcl",
"ttk/*",
"unsupported.tcl",
"xmfbox.tcl",
],
            "tkinter":[
"__init__.py",
"__main__.py",
"colorchooser.py",
"commondialog.py",
"constants.py",
"dialog.py",
"dnd.py",
"filedialog.py",
"font.py",
"messagebox.py",
"scrolledtext.py",
"simpledialog.py",
"tix.py",
"ttk.py",
]
      },
      long_description=long_description,
      license="OSI Approved :: Python Software Foundation License",
      install_requires=[],
      classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Android",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
    ],
     )

try:
    directory_path = lib+"/python3.12/lib-dynload"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    shutil.copy(root+'/_tkinter.cpython-312.so', lib+"/python3.12/lib-dynload")
    shutil.copytree(root+'/tcl86', lib+"/tcl8.6")
    shutil.copytree(root+'/tk86', lib+"/tk8.6")
    shutil.copytree(root+'/etc', os.environ['HOME']+"/etc")
except:
    pass


for item in sos:
    try:
        shutil.copy(root+'/'+item, lib)
    except:
        pass
