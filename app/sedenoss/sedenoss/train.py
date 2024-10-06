from .data import DataModule
from .models import FaSNet_base
from pytorch_lightning.cli import LightningCLI

import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    cli = LightningCLI(FaSNet_base, DataModule)