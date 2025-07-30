# Imports ==============================================================================

# Standard Library
from io import StringIO
from typing import Iterable, Pattern, NamedTuple
import csv
from itertools import combinations_with_replacement
from re import Match
import re

# Dependencies
from pyteomics.auxiliary import PyteomicsError
import glycowork.motif.tokenization as glycowork
import pyteomics.mass
import pyteomics.parser

# Constants ============================================================================

# NOTE: Not quite the monoisotopic water mass that the most accurate mass calculators
# produce, but it is what `glycowork` seems to be using
WATER_MASS: float = 18.0105546

# Types ================================================================================

type Regex = str | Pattern[str]


class Modification(NamedTuple):
    abbreviation: str
    targeted_residues: list[str]
    mass_delta: float


# NOTE: Inheriting from `NamedTuple` gives us the immutability we need to store these
# values in a `set`, and it also makes the fields easy to unpack!
class Glycan(NamedTuple):
    name: str
    mass: float


class Position(NamedTuple):
    start: int
    end: int


class Peptide(NamedTuple):
    sequence: str
    position: Position
    mass: float | None = None
    sites: tuple[str, ...] | None = None


class Glycopeptide(NamedTuple):
    sequence: str
    position: Position
    mass: float
    sites: tuple[str, ...]


# Functions ============================================================================


def glycan_mass(glycan_name: str) -> float:
    mass = 0.0

    # Try to parse the string as a fully-defined structure first
    try:
        mass = glycowork.glycan_to_mass(glycan_name)
    except (KeyError, IndexError):
        # But if that fails, then try just parsing it as a sugar composition
        try:
            mass = glycowork.composition_to_mass(glycan_name)
        except IndexError:
            pass

    # NOTE: Many nonsense structures / compositions just return the mass of water — if
    # the result was just a water mass, then whatever we were given wasn't valid, so
    # throw an error as if `mass` were never set
    if mass in [0, WATER_MASS]:
        raise ValueError(f"Invalid glycan structure / composition: '{glycan_name}'")
    else:
        return mass


def load_glycans(glycan_csv: str | None) -> set[Glycan]:
    expected_cols = ["Glycan", "Monoisotopic Mass"]

    if glycan_csv is None:
        return set()

    try:
        rows = csv.reader(StringIO(glycan_csv))
    except Exception as e:
        raise ValueError(f"Failed to read glycan CSV: {e}")

    header = next(rows)

    if header == expected_cols:
        return {Glycan(g, float(m)) for g, m in rows}
    elif header == expected_cols[:1]:
        return {Glycan(g, glycan_mass(g)) for (g,) in rows}
    else:
        raise ValueError(
            "The glycan file must contain either the columns "
            f"{expected_cols} or just {expected_cols[:1]}"
        )


def digest_protein(
    seq: str,
    rule: Regex,
    missed_cleavages: int,
    min_length: int | None,
    max_length: int | None,
    semi_enzymatic: bool,
) -> set[Peptide]:
    def build_peptide(index: int, sequence: str) -> Peptide:
        start = index + 1
        end = index + len(sequence)

        return Peptide(sequence, Position(start, end))

    if rule == "":
        return {build_peptide(0, seq)}

    return {
        build_peptide(*t)
        for t in pyteomics.parser.icleave(
            seq,
            rule,
            missed_cleavages,
            min_length,
            max_length,
            semi_enzymatic,
            None,
            True,
        )
    }


def modify_peptides(
    peptides: set[Peptide],
    modifications: Iterable[Modification],
    max_modifications: int | None,
) -> set[Peptide]:
    variable_modifications = {n: ts for (n, ts, _) in modifications}
    return {
        peptide._replace(sequence=isoform)
        for peptide in peptides
        for isoform in pyteomics.parser.isoforms(
            peptide.sequence,
            variable_mods=variable_modifications,
            max_mods=max_modifications,
        )
    }


def find_glycosylation_sites(
    peptides: set[Peptide], glycosylation_motif: Regex
) -> set[Peptide]:
    def find_sites(peptide: Peptide) -> tuple[str, ...]:
        if glycosylation_motif == "":
            return tuple()

        def name_site(match: Match[str]):
            residue = match.group()
            index = match.start() + peptide.position.start

            index -= sum(c.islower() for c in peptide.sequence[:index])

            return f"{residue}{index}"

        # NOTE: This is a `tuple` and not a `list` or `set` because only `tuple`s are hashable! It needs to be a
        # hashable type so that it can be collected into a `set`!
        return tuple(
            name_site(m) for m in re.finditer(glycosylation_motif, peptide.sequence)
        )

    return {p._replace(sites=find_sites(p)) for p in peptides}


def filter_glycopeptide_candidates(
    peptides: set[Peptide],
) -> set[Peptide]:
    return {p for p in peptides if p.sites is not None and len(p.sites) != 0}


def peptide_masses(
    peptides: set[Peptide], modifications: Iterable[Modification]
) -> set[Peptide]:
    def mass(peptide: Peptide) -> float:
        modification_masses = {n: m for (n, _, m) in modifications}
        aa_mass = pyteomics.mass.std_aa_mass | modification_masses
        try:
            return pyteomics.mass.fast_mass2(peptide.sequence, aa_mass=aa_mass)
        except PyteomicsError as e:
            raise ValueError(
                f"Unknown amino acid residue found in '{peptide.sequence}': {e.message}"
            )

    return {peptide._replace(mass=mass(peptide)) for peptide in peptides}


def to_glycopeptide(peptide: Peptide) -> Glycopeptide:
    sequence, position, mass, sites = peptide

    # Ensure the `Peptide` is fully initialized
    assert mass is not None
    assert sites is not None

    return Glycopeptide(sequence, position, mass, sites)


def build_glycopeptide(
    peptide: Peptide, glycans: set[Glycan], max_glycans: int | None
) -> set[Glycopeptide]:
    glycopeptide = to_glycopeptide(peptide)

    def build(glycan_set: tuple[Glycan, ...]):
        name = f"{'+'.join(sorted(g.name for g in glycan_set))}-{glycopeptide.sequence}"
        # This is a condensation reaction, so remember to take away a water mass
        mass = sum(g.mass for g in glycan_set) + glycopeptide.mass - WATER_MASS

        return glycopeptide._replace(sequence=name, mass=mass)

    sites = len(glycopeptide.sites)
    max_glycan_count = sites if max_glycans is None else min(sites, max_glycans)

    return {
        build(g)
        for c in range(max_glycan_count)
        for g in combinations_with_replacement(glycans, c + 1)
    }


def build_glycopeptides(
    peptides: set[Peptide],
    glycans: set[Glycan],
    max_glycans: int | None,
    all_peptides: bool,
) -> set[Glycopeptide]:
    glycopeptides = {
        g
        for p in filter_glycopeptide_candidates(peptides)
        for g in build_glycopeptide(p, glycans, max_glycans)
    }

    if all_peptides or len(glycopeptides) == 0:
        glycopeptides |= {to_glycopeptide(p) for p in peptides}

    return glycopeptides


def convert_to_csv(glycopeptides: set[Glycopeptide]) -> str:
    csv_str = StringIO()
    writer = csv.writer(csv_str)
    writer.writerow(
        [
            "Structure",
            "Monoisotopic Mass",
            "Start Position",
            "End Position",
            "Glycosylation Sites",
        ]
    )

    def glycans_mass_name_then_start(g: Glycopeptide) -> tuple[bool, float, str, int]:
        return ("-" in g.sequence, g.mass, g.sequence, g.position.start)

    sorted_glycopeptides = sorted(
        glycopeptides, key=glycans_mass_name_then_start, reverse=True
    )

    for g in sorted_glycopeptides:
        # NOTE: This is a nasty hack for PGFinder, which expects a `|1` type suffix
        # after the name of each structure. Really, that's a design flaw in PGFinder,
        # but we'll fix it here for now...
        name = f"{g.sequence}|1"
        start, end = g.position
        mass = round(g.mass, 6)
        sites = ", ".join(g.sites)

        writer.writerow([name, mass, start, end, sites])

    return csv_str.getvalue()
