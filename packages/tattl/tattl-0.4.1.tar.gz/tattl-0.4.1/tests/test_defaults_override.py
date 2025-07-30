from dataclasses import dataclass, field


def my_dict_factory():
    return {"spam": 1.23, "ham": 4.56, "eggs": 7.89}


def my_list_factory():
    return [1, 1, 2, 3, 5, 8]


@dataclass
class Structure:
    foo: str = "AAA"
    bar: int = 123
    baz: bool = field(default=True)
    qux: list[str] = field(default_factory=list)
    cor: dict[str, float] = field(default_factory=my_dict_factory)
    gra: list[int] = field(default_factory=my_list_factory)


EXAMPLE_TOML = """
foo = "BBB"
bar = 234
baz = false
qux = [ "Hello", "World" ]
cor = { snork = 2.34, blarg = 5.67, wibble = 8.90 }
gra = [ 1, 121, 12321, 1234321 ]
"""


def test_example():
    import tattl
    import tomllib

    data = tattl.unpack_dict(tomllib.loads(EXAMPLE_TOML), Structure)
    print(data)
    assert data == Structure(
        foo="BBB",
        bar=234,
        baz=False,
        qux=["Hello", "World"],
        cor={"snork": 2.34, "blarg": 5.67, "wibble": 8.90},
        gra=[1, 121, 12321, 1234321],
    )
