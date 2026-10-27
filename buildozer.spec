[app]
title = Tracko
package.name = tracko
package.domain = org.tracko
source.dir = .
source.include_exts = py,png
source.exclude_dirs = backend,.github,bin
version = 1.0
requirements = python3,kivy==2.3.1
orientation = portrait
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
