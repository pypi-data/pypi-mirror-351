"""
A small package for generating
[PGFinder](https://github.com/Mesnage-Org/pgfinder)-compatible glycopeptide
databases.
"""

# Imports ======================================================================

# Standard Library
from io import StringIO
from typing import Iterable

# Dependencies
from pyteomics.fasta import Protein
import pyteomics.fasta

# Local Modules
from glam._lib import (
    Regex,
    Modification,
    load_glycans,
    digest_protein,
    modify_peptides,
    find_glycosylation_sites,
    peptide_masses,
    build_glycopeptides,
    convert_to_csv,
)

# Curated Exports ==============================================================

__all__ = [
    "Regex",
    "Modification",
    "DIGESTIONS",
    "GLYCOSYLATION_MOTIFS",
    "MODIFICATIONS",
    "generate_glycopeptides",
]

# Constants ====================================================================

DIGESTIONS: dict[str, str] = {
    "2-Nitro-5-Thiocyanatobenzoic Acid": r"\w(?=C)",
    "Arg-C Endopeptidase": r"R",
    "Asp-N Endopeptidase": r"\w(?=D)",
    "BNPS-Skatole": r"W",
    "CNBr": r"M",
    "Caspase-1": r"(?<=[FWYL]\w[HAT])D(?![PEDQKR])",
    "Caspase-10": r"(?<=IEA)D",
    "Caspase-2": r"(?<=DVA)D(?![PEDQKR])",
    "Caspase-3": r"(?<=DMQ)D(?![PEDQKR])",
    "Caspase-4": r"(?<=LEV)D(?![PEDQKR])",
    "Caspase-5": r"(?<=[LW]EH)D",
    "Caspase-6": r"(?<=VE[HI])D(?![PEDQKR])",
    "Caspase-7": r"(?<=DEV)D(?![PEDQKR])",
    "Caspase-8": r"(?<=[IL]ET)D(?![PEDQKR])",
    "Caspase-9": r"(?<=LEH)D",
    "Chymotrypsin (High Specificity)": r"([FY](?!P))|(W(?![MP]))",
    "Chymotrypsin (Low Specificity)": r"([FLY](?!P))|(W(?![MP]))|(M(?![PY]))|(H(?![DMPW]))",
    "Clostripain": r"R",
    "Elastase": r"[AVSGLI](?!P)",
    "Enterokinase": r"(?<=[DE]{3})K",
    "Factor Xa": r"(?<=[AFGILTVM][DE]G)R",
    "Formic Acid": r"D",
    "Glutamyl Endopeptidase": r"E",
    "Granzyme B": r"(?<=IEP)D",
    "Hydroxylamine": r"N(?=G)",
    "Iodosobenzoic Acid": r"W",
    "LysC": r"K",
    "Pepsin (pH 1.3)": r"((?<=[^HKR][^P])[^R](?=[FL][^P]))|((?<=[^HKR][^P])[FL](?=\w[^P]))",
    "Pepsin (pH 2.0)": r"((?<=[^HKR][^P])[^R](?=[FLWY][^P]))|((?<=[^HKR][^P])[FLWY](?=\w[^P]))",
    "Proline Endopeptidase": r"(?<=[HKR])P(?!P)",
    "Proteinase K": r"[AEFILTVWY]",
    "Staphylococcal Peptidase I": r"(?<=[^E])E",
    "Thermolysin": r"[^DE](?=[AFILMV][^P])",
    "Thrombin": r"((?<=G)R(?=G))|((?<=[AFGILTVM][AFGILTVWA]P)R(?=[^DE][^DE]))",
    "Trypsin": r"([KR](?!P))|((?<=W)K(?=P))|((?<=M)R(?=P))",
}
"""
A dictionary mapping common protein digestion treatments to the regular expressions
that describe their cleavage sites.  
"""

GLYCOSYLATION_MOTIFS: dict[str, str] = {"N": r"(?<![a-z])N(?=[a-z]*[^P][a-z]*[TS])"}
"""
A dictionary mapping common glycosylation types to regular expressions that
describe the sequence motifs they target.
"""


MODIFICATIONS: dict[str, Modification] = {
    "Methionine Oxidation": Modification("ox", ["M"], 15.994915),
    "Carbamidomethyl": Modification("cm", ["C"], 57.021464),
    "N-Deamidation": Modification("da", ["N"], 0.984016),
}
"""
A dictionary mapping common peptide modifications to a tuple that describes
their abbreviation, the residues they can modify, and their monoisotopic mass
delta. 
"""

# Functions ====================================================================


# FIXME: This docstring is still out of date / wrong!
def generate_glycopeptides(
    fasta: str,
    digestion: Regex = "",
    missed_cleavages: int = 0,
    min_length: int | None = None,
    max_length: int | None = None,
    semi_enzymatic: bool = False,
    glycans: str | None = None,
    motif: Regex = "",
    max_glycans: int | None = None,
    all_peptides: bool = False,
    modifications: Iterable[Modification] = [],
    max_modifications: int | None = None,
    **kwargs,
) -> list[tuple[str, str]]:
    """Generates (glyco)peptides from an input FASTA and CSV file of glycans.

    The only *required* input is a FASTA file containing one or more protein sequences.
    Typically, you'll also want to select a digestion method, provide a CSV file of
    glycans, and specify a glycosylation motif to attach them to. A number of other
    options are available for narrowing or broadening the search space.

    Parameters
    ----------
    fasta : str,
        FASTA text describing the protein sequence(s) to be digested. Note that this
        function ***does not*** read from the filesystem — you'll need to first load
        your FASTA file into a `str` using something like `pathlib.Path.read_text`.

    digestion : str or Pattern[str], default: ""
        A regular expression used to digest the protein into peptides. The protein will
        be cut right *after* the regex match. A number of digestions and their regexes
        are built-in (see `DIGESTIONS`).
    missed_cleavages : int, default: 0
        The maximum number of missed cleavages to allow during digestion.
    min_length : int or None, default: None,
        The minimum length peptide to include in the digest output.
    max_length : int or None, default: None,
        The maximum length peptide to include in the digest output.
    semi_enzymatic : bool, default: False,
        Whether to include the products of semi-specific cleavage. This effectively cuts
        every peptide at every position and includes the result in the digest output.

    glycans : str or None, default: None
        A CSV file containing a `Glycan` column and optionally a
        `Monoisotopic Mass` column. If only a `Glycan` column is present, then the
        strings within it will be interpreted as glycan structures in either Oxford or
        IUPAC notation, or compositions like `Hex(2)Pent(1)HexNAc(1)` (see the
        `glycowork` package for a list of supported sugars). If a `Monoisotopic Mass`
        column is present, then the strings in the `Glycan` column are left
        uninterpreted and act only as names for the provided masses. Note that this
        function ***does not*** read from the filesystem — you'll need to first load
        your FASTA file into a `str` using something like `pathlib.Path.read_text`.
    motif : str or Pattern[str], default: ""
        A regular expression describing the sequence motif for glycosylation. By
        default, only peptides containing this motif will be used to generate the final
        list of glycopeptides. A number of glycosylation motifs and their regexes are
        built-in (see `GLYCOSYLATION_MOTIFS`).
    max_glycans: int or None, default: None
        The maximum number of glycans to allow per peptide.
    all_peptides: bool, default: False
        Whether to include peptides without any detected glycosylation motifs. If set to
        `True`, then both glycosylated and non-glycosylated peptides will be included in
        the output.

    modifications: Iterable[Modification], default: []
        A list of modifications to apply to the digested peptides. Each modification has
        a *lowercase* abbreviation, a list of residues that it can be applied to, and a
        monoisotopic mass delta. A number of modifications are built-in (see
        `MODIFICATIONS`).
    max_modifications: int or None, default: None
        The maximum number of modifications to allow per peptide.
    """

    proteins = pyteomics.fasta.read(StringIO(fasta), use_index=False)
    loaded_glycans = load_glycans(glycans)

    def generate(protein: Protein) -> tuple[str, str]:
        filename = f"{protein.description}.csv"
        seq = protein.sequence

        peptides = digest_protein(
            seq, digestion, missed_cleavages, min_length, max_length, semi_enzymatic
        )
        # NOTE: Doing this first is important so that `find_glycosylation_sites` is
        # aware of modifications. Otherwise it will be possible to have N-residues that
        # are both modified and glycosylated (which isn't biologically possible)!
        modified_peptides = modify_peptides(peptides, modifications, max_modifications)
        massive_peptides = peptide_masses(modified_peptides, modifications)
        computed_peptides = find_glycosylation_sites(massive_peptides, motif)
        glycopeptides = build_glycopeptides(
            computed_peptides, loaded_glycans, max_glycans, all_peptides
        )

        csv = convert_to_csv(glycopeptides)
        return (filename, csv)

    return [generate(protein) for protein in proteins]
