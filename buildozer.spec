[app]

# (str) Title of your application
title = Noir SMC

# (str) Package name
package.name = noir_smc

# (str) Package domain (needed for android/ios packaging)
package.domain = org.noir.agent

# (str) Source code where the main.py live
source.dir = mobile_app

# (str) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,requests,urllib3,certifi,idna,chardet

# (str) Custom source folders for requirements
# Tweak this if you use any non-standard modules
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, WAKE_LOCK, SYSTEM_ALERT_WINDOW

# (int) Android API to use
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or external data storage (False)
android.private_storage = True

# (list) Services to run
# Use this for background processing
services = NoirService:mobile_app/service.py

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = lib/armeabi/libcrypto.so, lib/armeabi/libssl.so

# (str) Full name including package for the Android activity to use.
# android.entrypoint = org.noir.agent.NoirActivity

# (list) List of Java classes to add to the android project
# android.add_src =

# (list) List of Java files to add to the android project
# android.add_jars = 

# (list) List of Java dependencies to add (via Gradle)
# android.gradle_dependencies = 'com.google.firebase:firebase-ads:10.2.0'

# (list) List of Gradle repositories to add
# android.gradle_repositories = 

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess downloads or network errors
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only.
android.accept_sdk_license = True

# (str) Android entry point
# android.entrypoint = main.py

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifacts
build_dir = ./.buildozer

# (str) Path to bin directory
bin_dir = ./bin
