from pathlib import Path

from orca_parse.charge import charge
from orca_parse.enthalpy import enthalpy_eh
from orca_parse.entropy_correction import entropy_correction_eh
from orca_parse.fspe import fspe_eh
from orca_parse.gibbs_correction import gibbs_correction_eh
from orca_parse.gibbs_free_energy import gibbs_free_energy_eh
from orca_parse.mult import mult
from orca_parse.run_time import run_time_h
from orca_parse.tda import tda
from orca_parse.thermal_correction import thermal_correction_eh
from orca_parse.xyz import xyz
from orca_parse.zero_point_energy import zero_point_energy_eh


class OrcaOutput:
    def __init__(self, output_file: Path | str) -> None:
        self.output_file = Path(output_file)

        if not self.output_file.is_file():
            raise FileNotFoundError(f"ORCA output file '{self.output_file.resolve()}' not found")

        self._lines = None

    @property
    def lines(self) -> list[str]:
        """Cache lines in memory"""
        if not self._lines:
            self._lines = self.output_file.read_text().splitlines()
        return self._lines

    @property
    def xyz(self) -> str:
        """Last cartesian coordinates as an XYZ string."""
        return xyz(self.lines)

    @property
    def charge(self) -> int:
        """Total charge"""
        return charge(self.lines)

    @property
    def mult(self) -> int:
        """Multiplicity"""
        return mult(self.lines)

    @property
    def tda(self) -> bool:
        """Tamm-Dancoff approximation"""
        return tda(self.lines)

    @property
    def run_time_h(self) -> float:
        """Total run time in hours"""
        return run_time_h(self.lines)

    @property
    def enthalpy_eh(self) -> float:
        """Total Enthalpy in Hartree"""
        return enthalpy_eh(self.lines)

    @property
    def entropy_correction_eh(self) -> float:
        """Entropy correction in Hartree"""
        return entropy_correction_eh(self.lines)

    @property
    def fspe_eh(self) -> float:
        """Final single point energy in Hartree"""
        return fspe_eh(self.lines)

    @property
    def gibbs_correction_eh(self) -> float:
        """Gibbs free energy minus the electronic energy in Hartree"""
        return gibbs_correction_eh(self.lines)

    @property
    def gibbs_free_energy_eh(self) -> float:
        """Gibbs free energy in Hartree"""
        return gibbs_free_energy_eh(self.lines)

    @property
    def thermal_correction_eh(self) -> float:
        """Thermal correction in Hartree"""
        return thermal_correction_eh(self.lines)

    @property
    def zero_point_energy_eh(self) -> float:
        """Zero-point energy in Hartree"""
        return zero_point_energy_eh(self.lines)
