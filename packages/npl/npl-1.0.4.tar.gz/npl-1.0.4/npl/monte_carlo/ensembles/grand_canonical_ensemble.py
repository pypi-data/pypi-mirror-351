from ..mc_moves import InsertionMove, DeletionMove, DisplacementMove
from .canonical_ensemble import BaseEnsemble
from npl.utils.random_number_generator import RandomNumberGenerator
import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator
from typing import Optional
import logging


PLANCK_CONSTANT = 6.62607e-34  # 4.135667696e-15  #Planck's constant in m²kg/s
BOLTZMANN_CONSTANT_eV_K = 8.617333262e-5  # 1.38066e-23  # Boltzmann constant in J/K
BOLTZMANN_CONSTANT_J_K = 1.38066e-23

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrandCanonicalEnsemble(BaseEnsemble):
    def __init__(self,
                 atoms: Atoms,
                 calculator: Calculator,
                 mu : dict,
                 masses: dict,
                 species : list,
                 temperature : float,
                 moves: dict,
                 max_displacement: float,
                 min_max_insert: list[float],
                 volume: float = None,
                 operating_box: list[list[float]] = None,
                 z_shift: float = None,
                 surface_indices: list[float] = None,
                 user_tag: Optional[str] = None,
                 random_seed: Optional[int] = None,
                 traj_file: str = 'traj_test.traj',
                 trajectory_write_interval: Optional[int] = None,
                 outfile: str = 'outfile.out',
                 outfile_write_interval: int = 10) -> None:

        super().__init__(atoms=atoms,
                         calculator=calculator,
                         random_seed=random_seed,
                         traj_file=traj_file,
                         trajectory_write_interval=trajectory_write_interval,
                         outfile=outfile,
                         outfile_write_interval=outfile_write_interval)

        if operating_box:
            from ase.cell import Cell
            self.operating_box = operating_box
            self.volume = Cell(operating_box).volume
            self.z_shift = z_shift
        else:
            self.operating_box = atoms.get_cell()
            self.volume = volume if volume else atoms.get_volume()
            self.z_shift = None

        self.volume = self.volume*1e-30  # Converting the volume in meters
        self.masses = masses
        self.surface_indices = surface_indices if surface_indices else None
        self.initial_atoms = len(self.atoms)
        self.n_atoms = len(self.atoms)
        self.species = species
        self._temperature = temperature
        self._mu = mu
        self._beta = 1/(self._temperature*BOLTZMANN_CONSTANT_eV_K)
        self._beta_J = 1/(self._temperature*BOLTZMANN_CONSTANT_J_K)

        self.n_ins_del = moves[0]
        self.n_displ = moves[1]
        self.n_moves = self.n_ins_del + self.n_displ
        self.max_displacement = max_displacement
        self.min_distance, self.max_distance = min_max_insert

        self.initialize_outfile()

        self.frac_ins_del = self.n_ins_del/self.n_moves
        self.rng_move_choice = RandomNumberGenerator(seed=self._random_seed+1)
        self.rng_acceptance = RandomNumberGenerator(seed=self._random_seed+2)
        # Initialize GCMC moves
        self.insert_move = InsertionMove(species=self.species,
                                         operating_box=self.operating_box,
                                         z_shift=self.z_shift,
                                         seed=self._random_seed+3)
        self.deletion_move = DeletionMove(species=self.species,
                                          operating_box=self.operating_box,
                                          z_shift=self.z_shift,
                                          seed=self._random_seed+4)
        self.displace_move = DisplacementMove(species=self.species,
                                              seed=self._random_seed+5,
                                              constraints=atoms.constraints,
                                              max_displacement=self.max_displacement)

        # COUNTERS
        self.count_moves = {'Displacements' : 0, 'Insertions' : 0, 'Deletions' : 0}
        self.count_acceptance = {'Displacements' : 0, 'Insertions' : 0, 'Deletions' : 0}

    def initialize_outfile(self) -> None:
        """
        Initializes the output file by overwriting any existing content and writing a header.
        """
        try:
            with open(self._outfile, 'w') as outfile:
                # Write the header with proper formatting
                outfile.write("+-------------------------------------------------+\n")
                outfile.write("| Grand Canonical Ensemble Monte Carlo Simulation |\n")
                outfile.write("+-------------------------------------------------+\n\n")

                # Write simulation parameters
                outfile.write("Simulation Parameters:\n")
                outfile.write(f"  Temperature (K): {self._temperature}\n")
                outfile.write(f"  Volume (Å³): {self.volume:.3f}\n")
                outfile.write(f"  Chemical potentials: {self._mu}\n")
                outfile.write(f"  Number of Insertion-Deletion moves: {self.n_ins_del}\n")
                outfile.write(f"  Interval instance to accept an Insertion Move: "
                              f"{self.min_distance}-{self.max_distance} Å³\n")
                outfile.write(f"  Number of Displacement moves: {self.n_displ}\n")
                outfile.write(f"  Maximum Displacement distance: {self.max_displacement}\n\n")

                # Simulation start message
                outfile.write("Starting simulation...\n")
                outfile.write("-" * 60 + "\n")

                # Write table header
                outfile.write("{:<10} {:<10} {:<15} {:<20}\n".format(
                              "Step", "N_atoms", "Energy (eV)",
                              "Acceptance Ratios (Displ, Ins, Del)"))
        except IOError as e:
            logger.error(f"Failed to initialize output file '{self._outfile}': {e}")
            raise

    def write_outfile(self, step: int) -> None:
        """
        Write the step and energy to the output file.

        Args:
            step (int): The current step.
        """
        acceptance_ratios = np.array(list(self.count_acceptance.values())) / np.array(
                    list(self.count_moves.values())
                )
        try:
            with open(self._outfile, 'a') as outfile:
                outfile.write("{:<10} {:<10} {:<15.6f} {:<20}\n".format(
                    step,
                    self.n_atoms,
                    self.E_old,
                    ", ".join(f"{ratio*100:.1f}%" if not np.isnan(ratio)
                              else "N/A" for ratio in acceptance_ratios)
                ))
        except IOError as e:
            logger.error(f"Error writing to file {self._outfile}: {e}")

    def _acceptance_condition(self,
                              atoms_new: Atoms,
                              potential_diff: float,
                              delta_particles: int,
                              species: str) -> bool:
        """
        Determines whether to accept a trial move based on the potential energy difference and
        temperature.

        Args:
            potential_diff (float): The potential energy difference between the current and new
            configurations.

        Returns:
            bool: True if the trial move is accepted, False otherwise.
        """
        if delta_particles == 0:
            if potential_diff <= 0:
                return True
            else:
                p = np.exp(-potential_diff * self._beta)
                return p > self.rng_acceptance.get_uniform()

        # de Broglie wavelength in meters
        lambda_db = PLANCK_CONSTANT / np.sqrt(2 * np.pi * self.masses[species] * (1 / self._beta_J))

        if delta_particles == 1:  # Insertion move
            min_distance_surf = min(atoms_new.get_distances(-1, self.surface_indices, mic=True))
            if min_distance_surf > self.max_distance:
                return False
            added_atoms_indices = range(len(atoms_new)-1)
            min_distace_new = min(atoms_new.get_distances(-1, added_atoms_indices, mic=True))
            if min_distace_new < self.min_distance:
                return False
            db_term = (self.volume / ((self.n_atoms+1)*lambda_db**3))
            exp_term = np.exp(-self._beta * (potential_diff - self._mu[species]))
            p = db_term * exp_term
            logger.debug(f"Lambda_db: {lambda_db:.3e}, p: {p:.3e}, Beta: {self._beta:.3e}, "
                         f"Exp: {exp_term:.3e}, Exp Arg {potential_diff - self._mu[species]}, "
                         f"Potential diff: {potential_diff:.3e}, "
                         f"Delta_particles: {delta_particles}")

        elif delta_particles == -1:  # Deletion move
            db_term = (lambda_db**3*self.n_atoms / self.volume)
            exp_term = np.exp(-self._beta * (potential_diff + self._mu[species]))
            p = db_term * exp_term
            logger.debug(f"Lambda_db: {lambda_db:.3e}, p: {p:.3e}, Beta: {self._beta:.3e}, "
                         f"Exp: {exp_term:.3e}, Exp Arg {potential_diff - self._mu[species]}, "
                         f"Potential diff: {potential_diff:.3e}, "
                         f"Delta_particles: {delta_particles}")
        if p > 1:
            return True
        else:
            return p > self.rng_acceptance.get_uniform()

    def do_displ_move(self):
        self.count_moves['Displacements'] += 1
        return self.displace_move.do_trial_move(self.atoms)

    def do_ins_del_move(self):
        r2 = self.rng_move_choice.get_uniform()
        if r2 <= 0.5:
            self.count_moves['Insertions'] += 1
            return self.insert_move.do_trial_move(self.atoms)
        else:
            self.count_moves['Deletions'] += 1
            return self.deletion_move.do_trial_move(self.atoms)

    def do_trial_step(self, ):
        for move in range(self.n_moves):
            r1 = self.rng_move_choice.get_uniform()
            if r1 <= self.frac_ins_del:
                atoms_new, delta_particles, species = self.do_ins_del_move()
            else:
                atoms_new = self.do_displ_move()
                delta_particles = 0
                species = 'X'

            if not atoms_new:  # NOTE: be carful here
                continue

            E_new = self.compute_energy(atoms_new)
            delta_E = E_new - self.E_old
            if self._acceptance_condition(atoms_new, delta_E, delta_particles, species):
                self.atoms = atoms_new
                self.n_atoms = len(self.atoms)
                self.E_old = E_new
                if delta_particles == 0:
                    self.count_acceptance['Displacements'] += 1
                if delta_particles == 1:
                    self.count_acceptance['Insertions'] += 1
                if delta_particles == -1:
                    self.count_acceptance['Deletions'] += 1

    def compute_energy(self, atoms):
        return self._calculator.get_potential_energy(atoms)

    def run(self, steps):
        """
        Runs the Grand Canonical Monte Carlo simulation.

        Args:
            steps (int): The number of Monte Carlo steps to run.

        Returns:
            None
        """
        logger.info("+-------------------------------------------------+")
        logger.info("| Grand Canonical Ensemble Monte Carlo Simulation |")
        logger.info("+-------------------------------------------------+")
        logger.info("Simulation Parameters:")
        logger.info(f"Temperature (K): {self._temperature}")
        logger.info(f"Volume (Å³): {self.volume:.3f}")
        logger.info(f"Chemical potentials: {self._mu}")
        logger.info(f"Number of Insertion-Deletion moves: {self.n_ins_del}")
        logger.info(f"Interval instance to accept an Insertion Move: "
                    f"{self.min_distance}-{self.max_distance} Å³")
        logger.info(f"Number of Displacement moves: {self.n_displ}")
        logger.info(f"Maximum Displacement distance: {self.max_displacement}")
        logger.info(f"Number of Monte Carlo steps: {steps}")
        logger.info("Starting simulation...\n")

        logger.info("{:<10} {:<10} {:<15} {:<20}".format(
            "Step", "N_atoms", "Energy (eV)", "Acceptance Ratios (Displ, Ins, Del)"
        ))
        logger.info("-" * 60)

        self.E_old = self.compute_energy(self.atoms)

        for step in range(1, steps + 1):
            self.do_trial_step()

            if step % self._outfile_write_interval == 0:
                acceptance_ratios = np.array(list(self.count_acceptance.values())) / np.array(
                    list(self.count_moves.values())
                )
                logger.info("{:<10} {:<10} {:<15.6f} {:<20}".format(
                    step,
                    self.n_atoms,
                    self.E_old,
                    ", ".join(f"{ratio*100:.1f}%" if not np.isnan(ratio)
                              else "N/A" for ratio in acceptance_ratios)
                ))
                self.write_outfile(step)

            if step % self._trajectory_write_interval == 0:
                self.write_traj_file(self.atoms)

        # Final statistics
        logger.info("\nSimulation Complete.")
        logger.info("Final Statistics:")
        logger.info(f"Total Moves Attempted: {self.n_moves * steps}")
        logger.info(f"Acceptance Ratios: {self.count_acceptance}")
        logger.info(f"Final Energy (eV): {self.E_old:.6f}")
