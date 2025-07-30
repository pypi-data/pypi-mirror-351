"""
directory_utils.py

A utility module for managing directory operations.
Provides methods to check for the existence, creation, listing, removal,
renaming, moving, and copying of directories.
Each method is documented with its purpose, parameters, and return values.
"""

import os
import pwd
import shutil
from typing import Optional

from darca_exception.exception import DarcaException
from darca_log_facility.logger import DarcaLogger

# Initialize the logger
logger = DarcaLogger(name="directory_utils").get_logger()


class DirectoryUtilsException(DarcaException):
    """
    Custom exception for directory utility errors.
    Inherits from DarcaException to provide structured logging,
    metadata handling, and optional chaining of original exceptions.
    """

    def __init__(self, message, error_code=None, metadata=None, cause=None):
        super().__init__(
            message=message,
            error_code=error_code or "DIRECTORY_UTILS_ERROR",
            metadata=metadata,
            cause=cause,
        )


class DirectoryUtils:
    @staticmethod
    def directory_exist(path: str) -> bool:
        """
        Check if a directory exists.

        Args:
            path (str): The directory path to check.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        exists = os.path.isdir(path)
        logger.debug(f"Checked directory existence for '{path}': {exists}")
        return exists

    @staticmethod
    def create_directory(
        path: str,
        permissions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> bool:
        """
        Create a directory with optional permissions and ownership.

        Args:
            path (str): Path to create.
            permissions (int, optional): chmod-style permission
            bits (e.g., 0o755).
            user (str, optional): Username to set as owner
            (requires privileges).

        Returns:
            bool: True if created or already exists.

        Raises:
            DirectoryUtilsException
        """
        if DirectoryUtils.directory_exist(path):
            logger.debug(f"Directory already exists: {path}")
            return True

        try:
            os.makedirs(path)
            if permissions is not None:
                os.chmod(path, permissions)

            if user is not None:
                uid = pwd.getpwnam(user).pw_uid
                gid = pwd.getpwnam(user).pw_gid
                os.chown(path, uid, gid)

            logger.debug(f"Directory created: {path}")
            return True

        except Exception as e:
            raise DirectoryUtilsException(
                message=f"Failed to create directory: {path}",
                error_code="DIRECTORY_CREATION_ERROR",
                metadata={"path": path},
                cause=e,
            )

    @staticmethod
    def list_directory(path: str, recursive: bool = False) -> list:
        """
        List all entries in the specified directory.

        Args:
            path (str): The directory path to list.
            recursive (bool, optional): If True, returns all file paths
                                        recursively (relative to `path`).

        Returns:
            list: List of entries or file paths depending on the `recursive`
                  flag.

        Raises:
            DirectoryUtilsException: If the directory does not exist or
                                     listing fails.
        """
        if not DirectoryUtils.directory_exist(path):
            raise DirectoryUtilsException(
                message=f"Directory does not exist: {path}",
                error_code="DIRECTORY_NOT_FOUND",
                metadata={"path": path},
            )

        try:
            if not recursive:
                contents = os.listdir(path)
                logger.debug(f"Directory '{path}' contents: {contents}")
                return contents

            collected_files = []
            for root, _, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, path)
                    collected_files.append(relative_path)
            logger.debug(
                f"Recursively collected files in '{path}': {collected_files}"
            )
            return collected_files

        except Exception as e:
            raise DirectoryUtilsException(
                message=f"Failed to list directory: {path}",
                error_code="DIRECTORY_LISTING_ERROR",
                metadata={"path": path, "recursive": recursive},
                cause=e,
            )

    @staticmethod
    def remove_directory(path: str) -> bool:
        """
        Remove a directory and all its contents recursively.

        Args:
            path (str): The directory path to remove.

        Returns:
            bool: True if the directory was removed successfully.

        Raises:
            DirectoryUtilsException: If the directory does not exist
                                     or removal fails.
        """
        if not DirectoryUtils.directory_exist(path):
            raise DirectoryUtilsException(
                message=f"Directory does not exist: {path}",
                error_code="DIRECTORY_NOT_FOUND",
                metadata={"path": path},
            )

        try:
            shutil.rmtree(path)
            logger.debug(f"Removed directory: {path}")
            return True
        except Exception as e:
            raise DirectoryUtilsException(
                message=f"Failed to remove directory: {path}",
                error_code="DIRECTORY_REMOVE_ERROR",
                metadata={"path": path},
                cause=e,
            )

    @staticmethod
    def rename_directory(src: str, dst: str) -> bool:
        """
        Rename a directory from the source path to the destination path.

        Args:
            src (str): The current directory path.
            dst (str): The new directory path.

        Returns:
            bool: True if the directory was renamed successfully.

        Raises:
            DirectoryUtilsException: If validation or renaming fails.
        """
        if not DirectoryUtils.directory_exist(src):
            raise DirectoryUtilsException(
                message=f"Source directory does not exist: {src}",
                error_code="DIRECTORY_NOT_FOUND",
                metadata={"src": src},
            )
        if DirectoryUtils.directory_exist(dst):
            raise DirectoryUtilsException(
                message=f"Destination directory already exists: {dst}",
                error_code="DIRECTORY_ALREADY_EXISTS",
                metadata={"dst": dst},
            )

        try:
            os.rename(src, dst)
            logger.debug(f"Renamed directory from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise DirectoryUtilsException(
                message=f"Failed to rename directory from '{src}' to '{dst}'",
                error_code="DIRECTORY_RENAME_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )

    @staticmethod
    def move_directory(src: str, dst: str) -> bool:
        """
        Move a directory from the source path to the destination path.

        Args:
            src (str): The source directory path.
            dst (str): The destination directory path.

        Returns:
            bool: True if the directory was moved successfully.

        Raises:
            DirectoryUtilsException: If the move operation fails.
        """
        if not DirectoryUtils.directory_exist(src):
            raise DirectoryUtilsException(
                message=f"Source directory does not exist: {src}",
                error_code="DIRECTORY_NOT_FOUND",
                metadata={"src": src},
            )

        try:
            shutil.move(src, dst)
            logger.debug(f"Moved directory from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise DirectoryUtilsException(
                message=f"Failed to move directory from '{src}' to '{dst}'",
                error_code="DIRECTORY_MOVE_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )

    @staticmethod
    def copy_directory(src: str, dst: str) -> bool:
        """
        Recursively copy a directory from the source to the destination.

        Note:
            If the destination directory already exists, this function
            will not proceed.

        Args:
            src (str): The source directory path.
            dst (str): The destination directory path.

        Returns:
            bool: True if the directory was copied successfully.

        Raises:
            DirectoryUtilsException: If copy operation fails.
        """
        if not DirectoryUtils.directory_exist(src):
            raise DirectoryUtilsException(
                message=f"Source directory does not exist: {src}",
                error_code="DIRECTORY_NOT_FOUND",
                metadata={"src": src},
            )
        if DirectoryUtils.directory_exist(dst):
            raise DirectoryUtilsException(
                message=f"Destination directory already exists: {dst}",
                error_code="DIRECTORY_ALREADY_EXISTS",
                metadata={"dst": dst},
            )

        try:
            shutil.copytree(src, dst)
            logger.debug(f"Copied directory from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise DirectoryUtilsException(
                message=f"Failed to copy directory from '{src}' to '{dst}'",
                error_code="DIRECTORY_COPY_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )
