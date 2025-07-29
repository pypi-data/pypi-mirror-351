# cpp_to_compile_commands

## What does this do

This converts files from the microsoft `c_cpp_properties.json` file to a compilation database file.
This file can be read by everything, including clangd.

## Installation

You can find it on [pypi](https://pypi.org/)

## Usage

See `cpp_to_compile_commands --help`

## Features

Many thinsg are hard coded and not fully usable yet. I made some advanced featurs, that were needed for my use case. (like prefix folding, so that gcc prefixes get recognized by clang). If you need a feature, feel free to make an Issue or PR.

I used this to convert the `c_cpp_properties.json` file, that was created by platformio (and arduino toolchain). So if you provide `--cross` it also detectes the non standard inlcude paths and adds them. Most of this only works for gcc atm.
