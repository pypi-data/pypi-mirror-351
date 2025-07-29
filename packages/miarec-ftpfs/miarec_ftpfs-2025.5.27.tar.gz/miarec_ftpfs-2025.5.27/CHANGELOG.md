# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [v2025.5.27] - 2025-05-27

[v2025.5.27]: https://github.com/miarec/miarec_ftpfs/compare/v2024.3.1...v2025.5.27

### Changed

- Fix compatibility issue with FTP servers that return responses in multi-line format

## [v2024.3.1] - 2024-03-11

[v2024.3.1]: https://github.com/miarec/miarec_ftpfs/compare/v2024.1.2...v2024.3.1

### Changed

- Reuse SSL session bewteen control and data channels (fixes compatibility issue with the latest FileZilla Server)


## [v2024.1.2] - 2024-01-23

[v2024.1.2]: https://github.com/miarec/miarec_ftpfs/compare/v2024.1.1...v2024.1.2

### Changed

- Add unit tests for connection recovery
- Fix potential race condition and connection leakage under certain conditions

## [v2024.1.1] - 2024-01-15

[v2024.1.1]: https://github.com/miarec/miarec_ftpfs/compare/v2024.1.0...v2024.1.1

### Changed

- Add unit tests for FTP-over-TLS (FTPS)
- Add Implicit TLS support
- Fix bugs in FTPS implementation in `close()` and `seek()` methods
- Better error handling. All FTP protocol-specific and SSL errors are converted into corresponding `FSError` exception
- Automatically try to re-establish network connection to FTP server on the next operation when `RemoteConnectionError`. The original implementation required a re-creation of the `FTPFS` object to re-connect.
- Add `move()` method using `FTP RENAME` command
- Fix connection leak when `FTPFile` is created directly (as opposed to within context manager) and is being destroyed by garbage collector without calling `close()` method.


## [v2024.1.0] - 2024-01-08

### Changed

- Extract FTPFS code from [pyFileSystem2](https://github.com/PyFilesystem/pyfilesystem2) project (version 2.4.16, released on 2022-05-02)
- Rename opener protocols from `ftp://` / `ftps://` to `mftp://` and `mftps://`
