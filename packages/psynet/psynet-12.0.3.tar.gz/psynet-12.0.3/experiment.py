import json
import os
from pathlib import Path
import psynet.experiment
from psynet.consent import NoConsent, MainConsent
from psynet.page import InfoPage, SuccessfulEndPage
from psynet.timeline import Timeline, CodeBlock
from psynet.timeline import Timeline, CodeBlock
from .tone_in_noise import ToneInNoiseNode, ToneInNoiseTrial
from psynet.trial.staircase import (
    GeometricStaircaseTrialMaker,
)
from psynet.asset import CachedAsset
from .speech_in_noise import SpeechInNoiseNode, SpeechInNoiseTrial
from psynet.asset import LocalStorage
from .customconsent import CustomMainConsent
from psynet.page import  VolumeCalibration

from psynet.utils import get_logger, get_translator, NoArgumentProvided
from .headphonetest import HugginsHeadphoneTest
from .instructions import tone_instructions, speech_instructions, FirstInstructions
from .demographics import Demography, ID_question, initials_question
from psynet.demography.general import EncounteredTechnicalProblems
from .speech_in_noise import get_lists_and_explentations, choose_list
from .calibration import CalibrationTrialMaker, CalibrationTrial, CalibrationNode, VolumeCalibrationOldeburg
from .ear_check_test import EarHeadphoneTest

# Ensure we're in the correct directory
EXPERIMENT_DIR = Path(__file__).parent.absolute()
os.chdir(EXPERIMENT_DIR)

ONE_EAR_ONLY = False
DEBUG_PARAMETERS = False

LANGUAGE = 'german' # for speech in noise
LOCALE = 'de'
WAGE_PER_HOUR = 9

# ... rest of the existing code ...
