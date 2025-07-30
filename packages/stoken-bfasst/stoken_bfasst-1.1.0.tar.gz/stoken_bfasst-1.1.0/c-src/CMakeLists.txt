cmake_minimum_required(VERSION 3.9)

project(stoken_bfasst VERSION 1.0.1 DESCRIPTION "stoken_bfasst")

add_library(stoken_bfasst SHARED
    src/stoken_bfasst.c
)

set_target_properties(stoken_bfasst PROPERTIES
    PUBLIC_HEADER src/stoken_bfasst.h
    OUTPUT_NAME "lib_stoken_bfasst"
    PREFIX ""
)

target_include_directories(stoken_bfasst PRIVATE include)
target_include_directories(stoken_bfasst PRIVATE src)

find_package(OpenSSL REQUIRED)
target_link_libraries(stoken_bfasst OpenSSL::SSL)
