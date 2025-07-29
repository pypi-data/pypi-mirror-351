"""
Models for representing genomic elements.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    """A position in the genome."""

    chrom: str
    chrom_start: int
    chrom_stop: int
    is_forward_strand: bool

    def __str__(self) -> str:
        return f"{self.chrom}[{self.chrom_start}:{self.chrom_stop}]"


@dataclass
class Gene:
    name: str


class Transcript:
    """RefGene Transcripts for hg19

    A gene may have multiple transcripts with different combinations of exons.
    """

    def __init__(
        self,
        name: str,
        version: Optional[int],
        gene: str,
        tx_position: Position,
        cds_position: Position,
        is_default=False,
        exons: Optional[list["Exon"]] = None,
    ):
        self.name = name
        self.version = version
        self.gene = Gene(gene)
        self.tx_position = tx_position
        self.cds_position = cds_position
        self.is_default = is_default
        self.exons = exons if exons else []

    @property
    def full_name(self) -> str:
        if self.version is not None:
            return f"{self.name}.{self.version}"
        else:
            return self.name

    @property
    def is_coding(self) -> bool:
        # Coding transcripts have CDS with non-zero length.
        return self.cds_position.chrom_stop - self.cds_position.chrom_start > 0

    @property
    def strand(self):
        return "+" if self.tx_position.is_forward_strand else "-"

    @property
    def coding_exons(self):
        return [exon.get_as_interval(coding_only=True) for exon in self.exons]


@dataclass
class BED6Interval:
    chrom: str
    chrom_start: int
    chrom_end: int
    name: str
    score: str
    strand: str

    def distance(self, offset: int):
        """Return the distance to the interval.

        if offset is inside the exon, distance is zero.
        otherwise, distance is the distance to the nearest edge.

        distance is positive if the exon comes after the offset.
        distance is negative if the exon comes before the offset.
        """

        start = self.chrom_start + 1
        end = self.chrom_end

        if start <= offset <= end:
            return 0

        start_distance = start - offset
        end_distance = offset - end

        if abs(start_distance) < abs(end_distance):
            return start_distance
        else:
            return -end_distance


class Exon:
    def __init__(self, transcript: Transcript, tx_position: Position, exon_number: int):
        self.transcript = transcript
        self.tx_position = tx_position
        self.exon_number = exon_number
        self.name = f"{self.transcript.name}.{self.exon_number}"

    def get_as_interval(self, coding_only=False) -> Optional[BED6Interval]:
        """Returns the coding region for this exon as a BED6Interval.

        This function returns a BED6Interval objects containing  position
        information for this exon. This may be used as input for
        pybedtools.create_interval_from_list() after casting chrom_start
        and chrom_end as strings.

        coding_only: only include exons in the coding region

        """

        exon_start = self.tx_position.chrom_start
        exon_stop = self.tx_position.chrom_stop

        # Get only exon coding region if requested
        if coding_only:
            if (
                exon_stop <= self.transcript.cds_position.chrom_start
                or exon_start >= self.transcript.cds_position.chrom_stop
            ):
                return None
            exon_start = max(exon_start, self.transcript.cds_position.chrom_start)
            exon_stop = min(
                max(exon_stop, self.transcript.cds_position.chrom_start),
                self.transcript.cds_position.chrom_stop,
            )

        return BED6Interval(
            self.tx_position.chrom,
            exon_start,
            exon_stop,
            self.name,
            ".",
            self.strand,
        )

    @property
    def strand(self):
        strand = "+" if self.tx_position.is_forward_strand else "-"
        return strand
