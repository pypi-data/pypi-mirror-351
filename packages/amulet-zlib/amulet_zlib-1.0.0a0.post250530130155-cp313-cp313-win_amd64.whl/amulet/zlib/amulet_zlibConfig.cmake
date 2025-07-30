if (NOT TARGET amulet_zlib)
    message(STATUS "Finding amulet_zlib")

    set(amulet_zlib_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_zlib_LIBRARY NAMES amulet_zlib PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_zlib_LIBRARY: ${amulet_zlib_LIBRARY}")

    add_library(amulet_zlib SHARED IMPORTED)
    set_target_properties(amulet_zlib PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${amulet_zlib_INCLUDE_DIR}"
        IMPORTED_IMPLIB "${amulet_zlib_LIBRARY}"
    )
endif()
