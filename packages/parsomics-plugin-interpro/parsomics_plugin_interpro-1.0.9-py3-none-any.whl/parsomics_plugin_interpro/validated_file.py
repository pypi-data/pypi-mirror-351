from pathlib import Path
from typing import ClassVar

from parsomics_core.entities.files.validated_file import ValidatedFileWithGenome


class InterproTsvValidatedFile(ValidatedFileWithGenome):
    _VALID_FILE_TERMINATIONS: ClassVar[list[str]] = [
        "_interpro_out.tsv",
        "_interpro.tsv",
    ]

    @property
    def genome_name(self) -> str:
        file_name: str = Path(self.path).name

        for termination in InterproTsvValidatedFile._VALID_FILE_TERMINATIONS:
            file_name = file_name.removesuffix(termination)

        genome_name = file_name
        if genome_name is None:
            raise Exception(
                f"Failed at extracting genome name from interpro tsv file: {self.path}"
            )

        return genome_name
