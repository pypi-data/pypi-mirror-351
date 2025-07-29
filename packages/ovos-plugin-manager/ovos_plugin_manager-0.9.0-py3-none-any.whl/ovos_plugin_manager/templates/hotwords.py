"""
This is here to allow importing this module outside mycroft-core, plugins
using this import instead of mycroft can be used

The main use case is for plugins to be used across different projects
"""
from ovos_config import Configuration
from ovos_utils import classproperty
from ovos_utils.lang import standardize_lang_tag
from ovos_utils.process_utils import RuntimeRequirements


def msec_to_sec(msecs):
    """Convert milliseconds to seconds.

    Arguments:
        msecs: milliseconds

    Returns:
        int: input converted from milliseconds to seconds
    """
    return msecs / 1000


class HotWordEngine:
    """Hotword/Wakeword base class to be implemented by all wake word plugins.

    Arguments:
        key_phrase (str): string representation of the wake word
        config (dict): Configuration block for the specific wake word
        lang (str): language code (BCP-47)
    """

    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-US"):
        self.key_phrase = str(key_phrase).lower()
        mycroft_config = Configuration()
        if config is None:
            # NOTE there is a bug in upstream,
            # the correct key is "hotwords" not "hot_words"
            # in here we account for both, but it's doubtful anyone
            # is using "hot_words"
            config = mycroft_config.get("hotwords", {}) or \
                     mycroft_config.get("hot_words", {})
            config = config.get(self.key_phrase, {})
        self.config = config

        # rough estimate 1 phoneme per 2 chars
        self.num_phonemes = len(key_phrase) / 2 + 1
        phoneme_duration = msec_to_sec(config.get('phoneme_duration', 120))
        self.expected_duration = self.num_phonemes * phoneme_duration

        self.listener_config = mycroft_config.get("listener") or {}
        self.lang = standardize_lang_tag(self.config.get("lang", lang))

    @classproperty
    def runtime_requirements(self):
        """ skill developers should override this if they do not require connectivity
         some examples:
         IOT plugin that controls devices via LAN could return:
            scans_on_init = True
            RuntimeRequirements(internet_before_load=False,
                                 network_before_load=scans_on_init,
                                 requires_internet=False,
                                 requires_network=True,
                                 no_internet_fallback=True,
                                 no_network_fallback=False)
         online search plugin with a local cache:
            has_cache = False
            RuntimeRequirements(internet_before_load=not has_cache,
                                 network_before_load=not has_cache,
                                 requires_internet=True,
                                 requires_network=True,
                                 no_internet_fallback=True,
                                 no_network_fallback=True)
         a fully offline plugin:
            RuntimeRequirements(internet_before_load=False,
                                 network_before_load=False,
                                 requires_internet=False,
                                 requires_network=False,
                                 no_internet_fallback=True,
                                 no_network_fallback=True)
        """
        return RuntimeRequirements(internet_before_load=False,
                                   network_before_load=False,
                                   requires_internet=False,
                                   requires_network=False,
                                   no_internet_fallback=True,
                                   no_network_fallback=True)

    def found_wake_word(self, frame_data):
        """Check if wake word has been found.

        Checks if the wake word has been found. Should reset any internal
        tracking of the wake word state.

        Arguments:
            frame_data (binary data): Deprecated. Audio data for large chunk
                                      of audio to be processed. This should not
                                      be used to detect audio data instead
                                      use update() to incrementaly update audio
        Returns:
            bool: True if a wake word was detected, else False
        """
        return False

    def reset(self):
        """
        Reset the WW engine to prepare for a new detection
        """
        pass

    def update(self, chunk):
        """Updates the hotword engine with new audio data.

        The engine should process the data and update internal trigger state.

        Arguments:
            chunk (bytes): Chunk of audio data to process
        """

    def stop(self):
        """
        Perform any actions needed to shut down the wake word engine.
        This may include things such as unloading data or shutdown
        external processes.
        """

    def shutdown(self):
        """
        Compatibility wrapper for `self.stop`
        """
        self.stop()
