#!/bin/sh
set -eu
THREADS=${THREADS:-4}
apk add --no-cache build-base linux-headers cmake git python3 py3-gitpython mbedtls-dev mbedtls-static zlib-dev zlib-static rapidjson-dev pcre2-dev pkgconf file
mkdir -p /deps
cd /deps
git clone --depth 1 --branch curl-8_6_0 https://github.com/curl/curl.git curl
cmake -S curl -B curl/build -DCURL_USE_MBEDTLS=ON -DHTTP_ONLY=ON -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=OFF -DCURL_USE_LIBSSH2=OFF -DBUILD_CURL_EXE=OFF
cmake --build curl/build -j "$THREADS"
cmake --install curl/build
git clone --depth 1 --branch 0.8.0 https://github.com/jbeder/yaml-cpp.git yaml-cpp
cmake -S yaml-cpp -B yaml-cpp/build -DCMAKE_BUILD_TYPE=Release -DYAML_BUILD_SHARED_LIBS=OFF -DYAML_CPP_BUILD_TESTS=OFF -DYAML_CPP_BUILD_TOOLS=OFF
cmake --build yaml-cpp/build -j "$THREADS"
cmake --install yaml-cpp/build
git clone --no-checkout https://github.com/ftk/quickjspp.git
cd quickjspp
git checkout 0c00c48895919fc02da3f191a2da06addeb07f09
git submodule update --init
cmake -DCMAKE_BUILD_TYPE=Release .
cmake --build . --target quickjs -j "$THREADS"
install -d /usr/lib/quickjs /usr/include/quickjs
install -m644 quickjs/libquickjs.a /usr/lib/quickjs/
install -m644 quickjs/quickjs.h quickjs/quickjs-libc.h /usr/include/quickjs/
install -m644 quickjspp.hpp /usr/include/
cd /deps
git clone https://github.com/PerMalmberg/libcron.git
cd libcron
git checkout ee34810b11bd23c8be637345532f91059b68b2d7
git submodule update --init
cmake -DCMAKE_BUILD_TYPE=Release .
cmake --build . --target libcron -j "$THREADS"
install -m644 libcron/out/Release/liblibcron.a /usr/lib/
install -d /usr/include/libcron /usr/include/date
install -m644 libcron/include/libcron/* /usr/include/libcron/
install -m644 libcron/externals/date/include/date/* /usr/include/date/
cd /deps
git clone --depth 1 --branch v4.3.0 https://github.com/ToruNiina/toml11.git
cmake -S toml11 -B toml11/build -DCMAKE_CXX_STANDARD=11
cmake --install toml11/build
