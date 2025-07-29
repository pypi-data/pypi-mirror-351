# tomlkit over toml because it preserves format/comments
from dataclasses import dataclass
from typing import Optional


@dataclass
class DiffDeps:
    extra: set
    missing: set

    def __str__(self):
        r = []
        if self.extra:
            r.extend(f'- {r}' for r in self.extra)
        if self.missing:
            r.extend(f'+ {r}' for r in self.missing)
        return '\n'.join(r)


@dataclass
class DiffVersion:
    pipfile: str
    pyproject: str


@dataclass
class Diff:
    deps: Optional[DiffDeps] = None
    version: Optional[DiffVersion] = None

    @property
    def empty(self) -> bool:
        return all(
            x is None
            for x in (
                self.deps,
                self.version,
            )
        )
