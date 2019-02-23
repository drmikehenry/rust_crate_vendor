rust_crate_vendor
=================

``rust_crate_vendor`` is a tool for expanding Rust crates into a form suitable
for use with Cargo.  This is especially helpful for offline installations of
Rust, where `crates.io <https://crates.io>`_ is not available.

Rust crates are distributed as ``crate_name-x.y.z.crate`` files, one for each
version ``x.y.z`` of a given ``crate_name``.  Typically these are downloaded
when using cargo to build or install Rust-based projects.  Cargo stores the
downloaded crates and associated metadata from crates.io in a local directory;
on unix systems, this is typically ``~/.cargo/registry/``.

Cargo supports the concept of "`source replacement`_" to replace one source of
crates with another.  For offline use, the official crates.io source can be
replaced with a local set of crate files.

.. _source replacement:
  https://doc.rust-lang.org/cargo/reference/source-replacement.html

The simplest form of source replacement is a "directory source".  The purpose of
``rust_crate_vendor`` is to populate a directory source based on a collection of
individual crate files.

Acquiring crate files
=====================

The simplest way to get crate files is to create a Rust project and add the
crates as dependencies::

  cargo new crates
  cd crates

For example, to get version 1.0.2 of the ``void`` crate, use a ``Cargo.toml``
file something like this::

  [package]
  name = "crates"
  version = "0.1.0"
  authors = ["Your Name <you@your_domain.com>"]
  edition = "2018"

  [dependencies]
  void = "1.0.2"
  # Or leave the version empty to get the latest:
  # void = ""

Cargo will cache the downloaded crates; for the above example, the crate will be
downloaded here::

    ~/.cargo/registry/cache/github.com-1ecc6299db9ec823/void-1.0.2.crate

Setting up an offline directory source
======================================

- First, collect the desired set of crate files.  For example::

    cd ~/.cargo/registry/cache/github.com-1ecc6299db9ec823/
    tar -zcf ~/crates.tar.gz .

- Transfer ``crates.tar.gz`` to the offline system.

- On the offline system, create an area for the crate files (``vendor.crates/``)
  and the directory source (``vendor/``) in the ``~/.cargo/`` directory::

    mkdir -p ~/.cargo/vendor.crates ~/.cargo/vendor

- Extract the transferred crates into ``~/.cargo/vendor.crates``::

    tar -C ~/.cargo/vendor.crates -zxf ~/crates.tar.gz

- Use ``rust_crate_vendor`` to create the ``~/.crates/vendor/`` tree::

    rust_crate_vendor ~/.cargo/vendor.crates ~/.cargo/vendor

- Create ``~/.cargo/config`` to replace the crates.io source with the
  ``vendor/`` directory source::

    cat > ~/.cargo/config <<EOF
    [source.crates-io]
    replace-with = "vendor"

    [source.vendor]
    directory = "$HOME/.cargo/vendor"
    EOF

Now you are ready to use Cargo.

Directory source structure
==========================

To create a directory source, the contents of each crate file must be extracted
into its own directory.  A crate file is packaged as a tarred-and-gzipped
archive containing the original source tree.  Integrity of the crate file and
the contained source files is verified by per-file SHA256 hash values which are
stored in a ``.cargo-checksum.json`` file within each unpacked crate.
``rust_crate_vendor`` extracts each crate file and generates a corresponding
``.cargo-checksum.json`` file.

For example, consider the ``void-1.0.2.crate`` file mentioned above.  When
unpacked via ``rust_crate_vendor``, it will generate the following tree of
files::

  vendor/void-1.0.2/src/lib.rs
  vendor/void-1.0.2/.travis.yml
  vendor/void-1.0.2/Cargo.toml
  vendor/void-1.0.2/README.md
  vendor/void-1.0.2/.cargo-checksum.json
  vendor/void-1.0.2/.gitignore

The generated ``.cargo-checksum.json`` file will contain::

  {
    "files": {
      ".gitignore": "f58cbb29ee4ff8a030c1e32d3f4ac2b19753d7fdf8f72d050d4bda1353364fda",
      ".travis.yml": "ad9b1a707a5c6bcc7c43fddb17a76f633893b0e6fa6891d99415704ae5ca58c2",
      "Cargo.toml": "ea686f87a150a8e43c4b7db57c56d3eda2a4963420d5570d91d99d7d610dd3fb",
      "README.md": "f85783a6fcf9ecc19edabd710775a88430d9e886f46728bfd7d65cef55ff3e73",
      "src/lib.rs": "7ab8269f30715c0729b0e04e5a09be4c413664dc4b530746ea3240ac80a64c66"
    },
    "package": "6a02e4885ed3bc0f2de90ea6dd45ebcbb66dacffe03547fadbb0eeae2770887d"
  }

References
==========

The following references were helpful in figuring out how to create a value
directory source:

- https://wiki.debian.org/Teams/RustPackaging/Policy
- https://wiki.debian.org/PortsDocs/BootstrappingRust
