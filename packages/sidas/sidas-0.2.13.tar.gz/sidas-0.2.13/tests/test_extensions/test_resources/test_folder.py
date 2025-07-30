from pathlib import Path, PurePath
from typing import Any, ClassVar

from sidas.extensions.resources.aws import AwsAccount
from sidas.extensions.resources.folder import InMemoryFolder, LocalFolder, S3Bucket


def test_s3_bucket_path() -> None:
    BUCKET_NAME = "example-bucket"
    account = AwsAccount()
    folder = S3Bucket(account, BUCKET_NAME)

    assert folder.full_path(PurePath("some/path")) == Path("example-bucket/some/path")

    assert str(folder.full_path(PurePath("some/path"))) == "example-bucket/some/path"
    assert (
        f"s3://{folder.full_path(PurePath('some/path'))}"
        == "s3://example-bucket/some/path"
    )


def test_in_memory_file_read_write(tmp_path: Path) -> None:
    LINE = "some text"
    file_name = PurePath("test")
    folder = InMemoryFolder()

    with folder.open(file_name, mode="w") as f:
        f.write(LINE)

    with folder.open(file_name) as f:
        assert f.readline() == LINE


def test_local_file_full_path() -> None:
    path = LocalFolder(".").full_path(PurePath("some", "path"))
    assert path == Path("some", "path")

    path = LocalFolder("./base").full_path(PurePath("some", "path"))
    assert path == Path("base", "some", "path")


def test_local_file_read_write(tmp_path: Path) -> None:
    LINE = "some text"
    file_name = PurePath("test")
    folder = LocalFolder(tmp_path)

    with folder.open(file_name, mode="w") as f:
        f.write(LINE)

    with folder.open(file_name) as f:
        assert f.readline() == LINE


def test_local_file_read_write_subfolder(tmp_path: Path) -> None:
    LINE = "some text"
    file_name = PurePath("test", "with", "folders")
    folder = LocalFolder(tmp_path)

    with folder.open(file_name, mode="w") as f:
        f.write(LINE)

    with folder.open(file_name) as f:
        assert f.readline() == LINE


class A:
    x: ClassVar[list[Any]] = []
    y: ClassVar[str | None] = None
    z: ClassVar[Any] = None

    def __init__(self) -> None:
        self.__class__.x.append(self)


class B(A):
    y = "b"


class C(A):
    y = "c"


class D:
    def __init__(self):
        A.z = self


def test_class_var():
    b = B()
    c = C()
    d = D()

    assert A.x == [b, c]
    assert c.x == [b, c]

    assert b.y == "b"
    assert c.y == "c"

    assert b.z == d
    assert c.z == d
