"""Unit tests of the Version class"""
from pytest_container import Version
from pytest_container.runtime import _get_docker_version
from pytest_container.runtime import _get_podman_version
from pytest_container.runtime import OciRuntimeBase

import pytest

# pragma pylint: disable=missing-function-docstring


@pytest.mark.parametrize(
    "ver1,ver2",
    [
        (Version(1, 0, 2), Version(1, 0, 2)),
        (Version(2, 0), Version(2, 0, 0)),
    ],
)
def test_version_eq(ver1: Version, ver2: Version):
    assert ver1 == ver2


def test_incompatible_types_eq():
    assert Version(1, 2) != 3


def test_incompatible_types_cmp():
    with pytest.raises(TypeError) as ctx:
        # pragma pylint: disable=expression-not-assigned
        Version(1, 2) < 3

    assert "'<' not supported between instances of 'Version' and 'int'" in str(
        ctx.value
    )


@pytest.mark.parametrize(
    "ver1,ver2",
    [
        (Version(1, 0, 2), Version(1, 0, 1)),
        (Version(2, 0, 1), Version(1, 0, 1)),
        (Version(1, 5, 1), Version(1, 0, 1)),
        (Version(1, 0, 1), Version(1, 0, 1, "foobar")),
    ],
)
def test_version_ne(ver1: Version, ver2: Version):
    assert ver1 != ver2


@pytest.mark.parametrize(
    "ver,stringified",
    [
        (Version(1, 2), "1.2"),
        (Version(1, 2, 5), "1.2.5"),
        (Version(1, 2, 5, "sdf"), "1.2.5 build sdf"),
    ],
)
def test_version_str(ver: Version, stringified):
    assert str(ver) == stringified


@pytest.mark.parametrize(
    "larger,smaller",
    [
        (Version(1, 2, 3), Version(1, 2, 2)),
        (Version(1, 2, 3), Version(1, 1, 3)),
        (Version(1, 2, 3), Version(0, 2, 3)),
    ],
)
def test_version_ge_gt(larger: Version, smaller: Version):
    assert larger > smaller
    assert larger >= smaller
    # pragma pylint: disable=comparison-with-itself
    assert larger >= larger
    assert smaller >= smaller


@pytest.mark.parametrize(
    "larger,smaller",
    [
        (Version(1, 2, 3), Version(1, 2, 2)),
        (Version(1, 2, 3), Version(1, 1, 3)),
        (Version(1, 2, 3), Version(0, 2, 3)),
    ],
)
def test_version_le_lt(larger: Version, smaller: Version):
    assert smaller < larger
    assert smaller <= larger
    # pragma pylint: disable=comparison-with-itself
    assert larger <= larger
    assert smaller <= smaller


@pytest.mark.parametrize(
    "stdout,ver",
    [
        ("Docker version 1.12.6, build 78d1802", Version(1, 12, 6, "78d1802")),
        (
            "Docker version 20.10.12-ce, build 459d0dfbbb51",
            Version(20, 10, 12, "459d0dfbbb51"),
        ),
        (
            "Docker version 20.10.16, build aa7e414",
            Version(20, 10, 16, "aa7e414"),
        ),
        (
            "Docker version 1.13.1, build 7d71120/1.13.1",
            Version(1, 13, 1, "7d71120/1.13.1"),
        ),
    ],
)
def test_docker_version_extract(stdout: str, ver: Version):
    assert _get_docker_version(stdout) == ver


@pytest.mark.parametrize(
    "stdout,ver",
    [
        ("podman version 3.0.1", Version(3, 0, 1)),
        ("podman version 3.4.4", Version(3, 4, 4)),
        ("podman version 1.6.4", Version(1, 6, 4)),
        ("podman version 4.0.2", Version(4, 0, 2)),
    ],
)
def test_podman_version_extract(stdout: str, ver: Version):
    assert _get_podman_version(stdout) == ver


def test_container_runtime_parsing(host, container_runtime: OciRuntimeBase):
    """Test that we can recreate the output of
    :command:`$container_runtime_binary --version` from the attribute
    :py:attr:`~pytest_container.runtime.OciRuntimeBase.version`.

    """
    version_without_build = Version(
        major=container_runtime.version.major,
        minor=container_runtime.version.minor,
        patch=container_runtime.version.patch,
    )
    version_string = (
        host.run_expect([0], f"{container_runtime.runner_binary} --version")
        .stdout.strip()
        .lower()
    )

    assert (
        f"{container_runtime.runner_binary} version {version_without_build}"
        in version_string
    )

    if container_runtime.runner_binary == "docker":
        assert f"build {container_runtime.version.build}" in version_string
