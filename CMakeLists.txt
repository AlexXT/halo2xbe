# Game Title (original Xbox), statically recompiled

cmake_minimum_required(VERSION 3.25)
project(game LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# The SDK: the hk21x fork of XboxXBERecomp, with the local xbdm.dll support
# and the XDK 5455 signatures (the build the Halo 2 beta is) on top.
set(SDK "D:/mygame/XboxXBE-Recomp-fork" CACHE PATH "the XboxXBE-Recomp SDK")

# The third-party libraries the SDK fetches, taken from the local cache
# instead of the network: SDL3 3.4.16, imgui 1.91.0, zydis 4.1.1 and
# tomlplusplus 3.4.0 are exactly the versions the SDK pins, and the cache
# holds them already.
set(FETCHCONTENT_SOURCE_DIR_SDL3        "D:/mygame/deps-cache/SDL"        CACHE PATH "")
set(FETCHCONTENT_SOURCE_DIR_IMGUI        "D:/mygame/deps-cache/imgui"      CACHE PATH "")
set(FETCHCONTENT_SOURCE_DIR_ZYDIS        "D:/mygame/deps-cache/zydis"      CACHE PATH "")
set(FETCHCONTENT_SOURCE_DIR_TOMLPLUSPLUS "D:/mygame/deps-cache/tomlplusplus" CACHE PATH "")

include(${SDK}/cmake/XbeRecomp.cmake)

file(GLOB XBE_HOST_SOURCES CONFIGURE_DEPENDS src/*/*.cpp)
list(FILTER XBE_HOST_SOURCES EXCLUDE REGEX "/src/game/")

# partitions as xbe_symbols wrote them into config/game.toml
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS config/game.toml)
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/config/game.toml)
    file(STRINGS config/game.toml GAME_PARTITIONS REGEX "^partitions *=")
    string(REGEX MATCH "[0-9]+" GAME_PARTITIONS "${GAME_PARTITIONS}")
endif()
# no config yet: build.bat writes it with xbe_symbols, the change reconfigures
if(NOT GAME_PARTITIONS)
    set(GAME_PARTITIONS 8)
endif()

# target name = GAME_EXE in build.bat, xbe = GAME_XBE
# halo2debug.xbe is the game's debug build: it carries the whole pstencil
# engine (190 functions across rasterizer_xbox_stencilshadow_{compute,draw,
# helpers}.obj plus the per-pass variants in rasterizer_xbox_models.obj),
# where the retail build has none of it.
# The config the recompiler reads: game_hand.toml, the hand kept entries,
# which includes game.toml, the scan output xbe_symbols writes. The scan
# output is rewritten on every build, so it is never edited; what is written
# by hand lives in the file that includes it.
add_xbe_image(Game halo2debug.xbe game_hand.toml ${GAME_PARTITIONS} game)

# ---------------------------------------------------------------------------
# The tag library, lifted too.
#
# halo2tagdebug.xbe is the Xbox tag library as a standalone XBE -- the same
# code the game links, and it carries the pstencil *shader class* on top of
# the engine. It has no game entry point, so there is nothing to run; the
# point is the generated code, which is where the engine reads.
#
# The names come from the linker map, placed on the XBE by aligning each
# object file: an object's string constants are the same text in both links,
# and an object's code is laid out in source order in both, so the map's
# function list and the XBE's function list line up. See tools/name_by_order.py.
# ---------------------------------------------------------------------------
add_custom_target(recompile_tag
    COMMAND xbe_recomp config/tag.toml --xdk ${XBE_SDK_DIR}/xdk
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Recompiling halo2tagdebug.xbe (the tag library)"
    VERBATIM)

# launcher/icon.ico, when there is one: the game's icon too (resource 1, which the window class loads)
if(WIN32 AND EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/launcher/icon.ico)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/game_icon.rc "1 ICON \"${CMAKE_CURRENT_SOURCE_DIR}/launcher/icon.ico\"\n")
    target_sources(Game PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/game_icon.rc)
endif()
