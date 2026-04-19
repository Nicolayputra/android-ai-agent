[app]
title = Sovereign Core V5
package.name = sovereigncore
package.domain = org.antigravity
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 5.0.0
requirements = python3,kivy,requests,urllib3,certifi,idna,charset-normalizer

# (str) Prescribed orientation
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE, WAKE_LOCK, FOREGROUND_SERVICE

# (int) Target Android API
android.api = 33
android.minapi = 21

# (str) Android entry point
python_for_android.branch = master

# (list) Android service definitions
# (str) Name:Module
services = SovereignEngine:main.py

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Android additionnal libraries
android.add_libs_armeabi_v7a = lib/armeabi-v7a/libpy.so
android.add_libs_arm64_v8a = lib/arm64-v8a/libpy.so

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Prescribed orientation
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1
