# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.

class KernelVersion():
    """Linux kernel version representation class."""

    major: str
    minor: str
    patch: str
    build: str
    distro: str
    arch: str

    def _extract_with_build(self, version: str):
        main_part, secondary_part = version.split("-")

        self.major, self.minor, self.patch = main_part.split(".")

        # Short format of kernel version without distro and arch mentioned
        if secondary_part.isnumeric():
            self.build = secondary_part
            self.distro = ""
            self.arch = ""
            return

        # Long format of kernel version
        for iter in range(len(secondary_part)):
            if secondary_part[iter].isalpha():
                self.build = secondary_part[:iter - 1]
                suffix = secondary_part[iter:]
                # There is no information about arch when we have vzX suffix
                if suffix.startswith("vz"):
                    self.distro = suffix.split(".")[0]
                else:
                    self.distro, self.arch = suffix.rsplit(".", 1)
                break

    def _extract_no_build(self, version: str):
        self.build = ""
        self.major, self.minor, self.patch, self.distro, self.arch = version.split(".")

    def _remove_prefix(self, version: str):
        while not version[0].isdigit():
            version = version.split("-", 1)[-1]
        return version

    def __init__(self, version: str):
        """Initialize a KernelVersion object."""
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.build = 0
        self.distro = ""
        self.arch = ""

        version = self._remove_prefix(version)
        if "-" in version:
            self._extract_with_build(version)
        else:
            self._extract_no_build(version)

    def __str__(self):
        """Return a string representation of a KernelVersion object."""
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.build != "":
            result += f"-{self.build}"
        if self.distro != "":
            result += f".{self.distro}"
        if self.arch != "":
            result += f".{self.arch}"

        return result

    def __lt__(self, other):
        if self.major < other.major or self.minor < other.minor or self.patch < other.patch:
            return True

        for build_part_left, build_part_right in zip(self.build.split("."), other.build.split(".")):
            if int(build_part_left) < int(build_part_right):
                return True
            elif int(build_part_left) > int(build_part_right):
                return False

        return len(self.build) < len(other.build)

    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch and self.build == other.build

    def __ge__(self, other):
        return not self.__lt__(other)


class PHPVersion():
    """Php version representation class."""

    major: int
    minor: int

    def _extract_from_version(self, version: str):
        # Version string example is "7.2" or "7.2.24"
        major_part, minor_part = version.split(".")[:2]
        self.major = int(major_part)
        self.minor = int(minor_part)

    def _extract_from_desc(self, description: str):
        # Description string example is "PHP 5.2"
        major_part, minor_part = description.split(" ")[1].split(".")
        self.major = int(major_part)
        self.minor = int(minor_part)

    def _extract_from_plesk_package(self, packagename: str):
        # Related package name example is plesk-php52
        version_part = packagename.split("php")[1]
        self.major = int(version_part[0])
        self.minor = int(version_part[1])

    def __init__(self, to_extract: str):
        """Initialize a KernelVersion object."""
        self.major = 0
        self.minor = 0

        if to_extract.startswith("plesk-php"):
            self._extract_from_plesk_package(to_extract)
        elif to_extract.startswith("PHP "):
            self._extract_from_desc(to_extract)
        elif to_extract[0].isdigit():
            self._extract_from_version(to_extract)
        else:
            raise ValueError(f"Cannot extract php version from '{to_extract}'")

    def __str__(self):
        """Return a string representation of a PHPVersion object."""
        return f"PHP {self.major}.{self.minor}"

    def __lt__(self, other):
        return self.major < other.major or (self.major == other.major and self.minor < other.minor)

    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor

    def __ge__(self, other):
        return not self.__lt__(other)
