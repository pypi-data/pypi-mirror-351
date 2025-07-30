"""
file_utils.py

A utility module for managing file operations.
Provides methods to check for file existence, write, read, remove, rename,
move, and copy files.
Each method is documented with its purpose, parameters, and return values.
"""

import os
import pwd
import shutil
from typing import Optional, Union

from darca_exception.exception import DarcaException
from darca_log_facility.logger import DarcaLogger

from darca_file_utils.directory_utils import (
    DirectoryUtils,  # Importing directory utilities
)

# Initialize the logger
logger = DarcaLogger(name="file_utils").get_logger()


class FileUtilsException(DarcaException):
    """
    Custom exception for file utility errors.
    Inherits from DarcaException to provide structured logging,
    metadata handling, and optional chaining of original exceptions.
    """

    def __init__(self, message, error_code=None, metadata=None, cause=None):
        super().__init__(
            message=message,
            error_code=error_code or "FILE_UTILS_ERROR",
            metadata=metadata,
            cause=cause,
        )


class FileUtils:
    @staticmethod
    def file_exist(path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path (str): The file path to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        exists = os.path.isfile(path)
        logger.debug(f"Checked file existence for '{path}': {exists}")
        return exists

    @staticmethod
    def write_file(
        file_path: str,
        content: Union[str, bytes],
        *,
        binary: bool = False,  # ← explicit flag
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> bool:
        """
        Write *content* to *file_path*.

        Parameters
        ----------
        binary   : bool, default False
            • False - write as UTF-8 text.  *bytes* will be decoded first.
            • True  - write as raw bytes.   *str* will be UTF-8 encoded.
        permissions : int | None
            chmod bits (e.g. 0o644) applied after writing.
        user : str | None
            Username to chown the file to (requires privilege).

        Returns
        -------
        bool
            True on success.

        Raises
        ------
        FileUtilsException
            For directory creation, write, chmod, or chown errors.
        """
        # ---------- ensure parent directory exists --------------------- #
        directory = os.path.dirname(file_path)
        if directory and not DirectoryUtils.directory_exist(directory):
            logger.info(
                "Directory does not exist for file: %s – creating it.",
                directory,
            )
            if not DirectoryUtils.create_directory(
                directory, permissions=permissions, user=user
            ):
                raise FileUtilsException(
                    message="Failed to create directory for file writing.",
                    error_code="DIRECTORY_CREATION_FAILED",
                    metadata={"directory": directory},
                )

        # ---------- normalise content & pick mode ---------------------- #
        if binary:
            if isinstance(content, str):
                content = content.encode("utf-8")
            mode = "wb"
        else:
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            mode = "w"

        try:
            # ---------- actual write ----------------------------------- #
            with open(file_path, mode) as f:
                f.write(content)  # type: ignore[arg-type]

            if permissions is not None:
                os.chmod(file_path, permissions)

            if user is not None:
                pw = pwd.getpwnam(user)
                os.chown(file_path, pw.pw_uid, pw.pw_gid)

            logger.debug(
                "Wrote %s file: %s", "binary" if binary else "text", file_path
            )
            return True

        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to write to file: {file_path}",
                error_code="FILE_WRITE_ERROR",
                metadata={
                    "file_path": file_path,
                    "binary": binary,
                },
                cause=e,
            ) from e

    # ───────────────────────────── read_file ─────────────────────────── #
    @staticmethod
    def read_file(
        file_path: str,
        *,
        binary: bool = False,  # ← explicit flag
    ) -> Union[str, bytes]:
        """
        Read *file_path*.

        Parameters
        ----------
        binary : bool, default False
            • False - return UTF-8 text (str)
            • True  - return raw bytes

        Returns
        -------
        str | bytes
            File contents in the requested form.

        Raises
        ------
        FileUtilsException
            If the file does not exist or reading fails.
        """
        if not FileUtils.file_exist(file_path):
            raise FileUtilsException(
                message=f"File not found: {file_path}",
                error_code="FILE_NOT_FOUND",
                metadata={"file_path": file_path},
            )

        mode = "rb" if binary else "r"
        try:
            with open(
                file_path, mode, encoding=None if binary else "utf-8"
            ) as f:
                data = f.read()

            logger.debug(
                "Read %s file: %s", "binary" if binary else "text", file_path
            )
            return data

        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to read file: {file_path}",
                error_code="FILE_READ_ERROR",
                metadata={
                    "file_path": file_path,
                    "binary": binary,
                },
                cause=e,
            ) from e

    @staticmethod
    def remove_file(file_path: str) -> bool:
        """
        Remove the specified file.

        Args:
            file_path (str): The path to the file to be removed.

        Returns:
            bool: True if the file was removed successfully.

        Raises:
            FileUtilsException: If the file does not exist or
                                cannot be removed.
        """
        if not FileUtils.file_exist(file_path):
            raise FileUtilsException(
                message=f"File does not exist: {file_path}",
                error_code="FILE_NOT_FOUND",
                metadata={"file_path": file_path},
            )

        try:
            os.remove(file_path)
            logger.debug(f"Removed file: {file_path}")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to remove file: {file_path}",
                error_code="FILE_REMOVE_ERROR",
                metadata={"file_path": file_path},
                cause=e,
            )

    @staticmethod
    def rename_file(src: str, dst: str) -> bool:
        """
        Rename a file from the source path to the destination path.

        Args:
            src (str): The current file path.
            dst (str): The new file path.

        Returns:
            bool: True if the file was renamed successfully.

        Raises:
            FileUtilsException: If the source doesn't exist, destination
                                exists, or rename fails.
        """
        if not FileUtils.file_exist(src):
            raise FileUtilsException(
                message=f"Source file does not exist: {src}",
                error_code="FILE_NOT_FOUND",
                metadata={"src": src},
            )
        if FileUtils.file_exist(dst):
            raise FileUtilsException(
                message=f"Destination file already exists: {dst}",
                error_code="FILE_ALREADY_EXISTS",
                metadata={"dst": dst},
            )

        try:
            os.rename(src, dst)
            logger.debug(f"Renamed file from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to rename file from '{src}' to '{dst}'",
                error_code="FILE_RENAME_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )

    @staticmethod
    def move_file(src: str, dst: str) -> bool:
        """
        Move a file from the source path to the destination path.

        Args:
            src (str): The current file path.
            dst (str): The destination file path.

        Returns:
            bool: True if the file was moved successfully.

        Raises:
            FileUtilsException: If the source doesn't exist or move fails.
        """
        if not FileUtils.file_exist(src):
            raise FileUtilsException(
                message=f"Source file does not exist: {src}",
                error_code="FILE_NOT_FOUND",
                metadata={"src": src},
            )

        try:
            shutil.move(src, dst)
            logger.debug(f"Moved file from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to move file from '{src}' to '{dst}'",
                error_code="FILE_MOVE_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )

    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """
        Copy a file from the source path to the destination path.

        Args:
            src (str): The source file path.
            dst (str): The destination file path.

        Returns:
            bool: True if the file was copied successfully.

        Raises:
            FileUtilsException: If the source doesn't exist, destination
                                exists, or copy fails.
        """
        if not FileUtils.file_exist(src):
            raise FileUtilsException(
                message=f"Source file does not exist: {src}",
                error_code="FILE_NOT_FOUND",
                metadata={"src": src},
            )
        if FileUtils.file_exist(dst):
            raise FileUtilsException(
                message=f"Destination file already exists: {dst}",
                error_code="FILE_ALREADY_EXISTS",
                metadata={"dst": dst},
            )

        try:
            shutil.copy2(src, dst)
            logger.debug(f"Copied file from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to copy file from '{src}' to '{dst}'",
                error_code="FILE_COPY_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )
