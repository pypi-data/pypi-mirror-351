import pathlib
import logging
from constellaration import forward_model, initial_guess
from constellaration.boozer import boozer
from constellaration.utils import (
    file_exporter,
    visualization,
    visualization_utils,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

compact_boundary = initial_guess.generate_rotating_ellipse(
    aspect_ratio=3, elongation=0.5, rotational_transform=0.4, n_field_periods=3
)

settings = forward_model.ConstellarationSettings.default_high_fidelity_skip_qi()

compact_boundary_metrics, compact_boundary_equilibrium = forward_model.forward_model(
    compact_boundary, settings=settings
)

boozer_settings = boozer.BoozerSettings(normalized_toroidal_flux=[0.0, 0.25, 1])

logger.info("hello")

compact_boundary_boozer_plots = visualization.plot_boozer_surfaces(
    compact_boundary_equilibrium, settings=boozer_settings
)

compact_boundary_boozer_plots[0].show()
input("dsldsds")