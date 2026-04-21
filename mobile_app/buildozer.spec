[app]

# --- Identitas Aplikasi ---
title = Noir Sovereign v14
package.name = noirsmc
package.domain = org.antigravity
version = 14.0.0

# --- Sumber Kode ---
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.exclude_dirs = tests, bin, .buildozer

# --- Dependensi Python ---
# Hanya dependensi yang PASTI ada di python-for-android recipes
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,charset-normalizer,pyjnius

# --- Target Platform ---
android.api = 34
android.minapi = 26
android.accept_sdk_license = True

# --- Arsitektur (arm64-v8a adalah target utama Redmi Note 14) ---
android.archs = arm64-v8a

# --- Izin Sistem (Sovereign Control & Shizuku) ---
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,FOREGROUND_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA,RECEIVE_BOOT_COMPLETED,SYSTEM_ALERT_WINDOW,VIBRATE,POST_NOTIFICATIONS,moe.shizuku.manager.permission.API_V23

# --- Orientasi ---
orientation = portrait

# --- Fullscreen ---
fullscreen = 0

# --- Icon (Gunakan default jika belum ada) ---
# icon.filename = %(source.dir)s/data/icon.png

# --- Fitur Android ---
# android.features = 

# --- Branch python-for-android ---
p4a.branch = master

# --- Gradle ---
android.gradle_dependencies = com.android.support:support-v4:28.0.0

# --- Wearable API atau extras (kosong dulu) ---
# android.add_libs_armeabi_v7a =
# android.add_libs_arm64_v8a =

[buildozer]
log_level = 2
warn_on_root = 1
