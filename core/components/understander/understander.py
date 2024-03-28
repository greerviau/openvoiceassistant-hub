import time
import importlib
import typing
import random
import logging
logger = logging.getLogger("components.understander")
import nltk
nltk.download("wordnet")
from nltk.corpus import wordnet

from core import config
from core.enums import Components
from core.schemas import Context
from core.utils.nlp.preprocessing import clean_text, encode_command
from core.utils.nlp.information_extraction import extract_information
from core.utils.nlp.false_positives import FALSE_POSITIVES, add_false_positive

CANCEL_WORDS = ["stop", "cancel", "nevermind", "quiet", "shut up"]

class Understander:
    def __init__(self, ova: "OpenVoiceAssistant"):
        self.ova = ova
        understander_config = config.get(Components.Understander.value)
        self.conf_thresh = understander_config["conf_thresh"]
        augment_data_percent = understander_config["augment_intent_data_percent"]
        if augment_data_percent > 100:
            augment_data_percent = 100
            config.set(Components.Understander.value, "augment_intent_data_percent", augment_data_percent)
        elif augment_data_percent < 0:
            augment_data_percent = 0
            config.set(Components.Understander.value, "augment_intent_data_percent", augment_data_percent)

        imported_skills = list(config.get("skills").keys())
        self.intents, n_samples = self.load_intents(imported_skills)
        self.vocab_list = self.load_vocab(self.intents.values())
        augmented_intents = self.add_negative_samples(self.intents, n_samples)
        if augment_data_percent > 0:
            augmented_intents = self.augment_data(augmented_intents, self.vocab_list, augment_data_percent)

        positive_samples = 0
        negative_samples = 0
        for tag, patterns in augmented_intents.items():
            if tag == "NO_COMMAND-NO_ACTION":
                negative_samples += len(patterns)
            else:
                positive_samples += len(patterns)

        logger.info(f"Positive Sampels: {positive_samples}")
        logger.info(f"Negative Sampels: {negative_samples}")
        
        self.use_keyword_matching = understander_config["use_keyword_matching"]
        logger.info(f"Use keyword matching: {self.use_keyword_matching}")
    
        self.algo = understander_config["algorithm"].lower().replace(" ", "_")
        self.module = importlib.import_module(f"core.components.understander.{self.algo}")

        self.verify_algo_config()

        algo_config = config.get(Components.Understander.value, "config")

        self.engine = self.module.build_engine(algo_config, augmented_intents, ova)

    def verify_algo_config(self):
        current_config = config.get(Components.Understander.value, "config")
        default_config = self.module.default_config()
        try:
            if not current_config or (current_config.keys() != default_config.keys()) or current_config["id"] != default_config["id"]:
                raise RuntimeError("Incorrect config")
        except:
            config.set(Components.Understander.value, "config", default_config)

    def load_intents(self, imported_skills: typing.List):
        tagged_intents = {}
        pattern_count = 0
        for skill in imported_skills:
            intents = self.ova.skill_manager.get_skill_intents(skill).copy()
            for intent in intents:
                tag = intent["action"]
                patterns = intent["patterns"].copy()
                pattern_count += len(patterns)
                label = f"{skill}-{tag}"
                tagged_intents[label] = patterns
        
        return tagged_intents, pattern_count

    def load_vocab(self, all_patterns: typing.List[typing.List[str]]):
        words = []
        words.extend(CANCEL_WORDS)
        for patterns in all_patterns:
            for pattern in patterns:
                words.extend([clean_text(word) for word in pattern.split()])
        return list(set(words))

    def add_negative_samples(self, intents: typing.Dict, n_samples: int):
        false_positives = list(set([encode_command(sample, self.vocab_list) for sample in FALSE_POSITIVES]))
        random.shuffle(false_positives)
        n_false_samples = n_samples
        if len(false_positives) > n_false_samples:
            false_samples = false_positives[:n_false_samples]
        else:
            false_samples = false_positives
        intents["NO_COMMAND-NO_ACTION"] = false_samples
        return intents
    
    def augment_data(self, intents: typing.Dict, vocab_list: typing.List[str], augment_data_percent:float):
        logger.info(f"Augmenting {augment_data_percent}% of data")
        def get_synonyms(word):
            synonyms = set()
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    synonyms.add(lemma.name())
            return list(synonyms)

        synonym_map = {word: get_synonyms(word) for word in vocab_list}

        augmented_intents = {}
        for tag, patterns in intents.items():
            augmented_patterns = patterns.copy()  # Make a shallow copy to avoid modifying the original list

            # Augment data by randomly replacing words with BLANK
            for pattern in patterns:
                if random.random() < augment_data_percent:
                    words = pattern.split()
                    num_words = len(words)
                    if num_words > 3:
                        num_blanks = min(2, num_words)  # Choose a maximum of 2 words to replace with BLANK
                        for _ in range(num_blanks):
                            index = random.randint(0, num_words - 1)
                            words[index] = "BLANK"
                        augmented_patterns.append(" ".join(words))
                    else:
                        augmented_patterns.append(pattern)

            # Augment data by randomly removing words from each pattern
            for pattern in patterns:
                if random.random() < augment_data_percent:
                    words = pattern.split()
                    num_words = len(words)
                    if num_words > 3:
                        num_words_to_remove = max(1, int(0.1 * num_words))  # Remove up to 10% of words
                        for _ in range(num_words_to_remove):
                            if words:
                                index = random.randint(0, len(words) - 1)
                                del words[index]
                        augmented_patterns.append(" ".join(words))
                    else:
                        augmented_patterns.append(pattern)

            # Random BLANK Insertion
            for pattern in patterns:
                if random.random() < augment_data_percent:
                    words = pattern.split()
                    num_words = len(words)
                    if num_words > 3:
                        num_insertions = min(2, num_words)  # Choose a maximum of 2 words to insert
                        for _ in range(num_insertions):
                            index = random.randint(0, num_words)
                            inserted_word = "BLANK"
                            words.insert(index, inserted_word)
                        augmented_patterns.append(" ".join(words))
                    else:
                        augmented_patterns.append(pattern)
            
            # Random Word Insertion
            """
            for pattern in patterns:
                words = pattern.split()
                num_words = len(words)
                num_insertions = min(2, num_words)  # Choose a maximum of 2 words to insert
                for _ in range(num_insertions):
                    index = random.randint(0, num_words)
                    inserted_word = random.choice(vocab_list)
                    words.insert(index, inserted_word)
                augmented_patterns.append(" ".join(words))
            """

            # Random Swap
            for pattern in patterns:
                if random.random() < augment_data_percent:
                    words = pattern.split()
                    num_words = len(words)
                    if num_words > 3:
                        index1, index2 = random.sample(range(num_words), 2)
                        words[index1], words[index2] = words[index2], words[index1]
                        augmented_patterns.append(" ".join(words))
                    else:
                        augmented_patterns.append(pattern)

            # Random Synonym Replacement
            for pattern in patterns:
                if random.random() < augment_data_percent:
                    words = pattern.split()
                    if len(words) > 3:
                        for i, word in enumerate(words):
                            if random.random() < 0.1:  # Probability of 10% for replacement
                                if word in synonym_map:
                                    synonyms = synonym_map[word]
                                    if synonyms:
                                        words[i] = random.choice(synonyms)
                        augmented_patterns.append(" ".join(words))
                    else:
                        augmented_patterns.append(pattern)

            augmented_intents[tag] = augmented_patterns

        return augmented_intents
    
    def get_algorithm_default_config(self, algorithm_id: str) -> typing.Dict:
        try:
            module = importlib.import_module(f"core.components.understander.{algorithm_id}")
            return module.default_config()
        except Exception as e:
            raise RuntimeError("Understander algorithm does not exist")

    def run_stage(self, context: Context):
        logger.info("Understanding Stage")
        start = time.time()

        time_sent = context["time_sent"]
        last_time_engaged = context["last_time_engaged"]

        delta_time = time_sent - last_time_engaged
        
        command = context["command"]

        context["sent_info"] = extract_information(command)

        try:
            cleaned_command = context["cleaned_command"]
        except KeyError:
            cleaned_command = clean_text(command)
            context["cleaned_command"] = cleaned_command
            logger.info(f"Cleaned Command: {cleaned_command}")

        encoded_command = encode_command(cleaned_command, self.vocab_list)
        context["encoded_command"] = encoded_command
        logger.info(f"Encoded command: {encoded_command}")
        
        skill, action, conf, run_action = "", "", 0, False
        if encoded_command in ["", "BLANK"]:
            skill = "NO_COMMAND"
            action = "NO_ACTION"
            conf = 100
            run_action = False
        elif encoded_command in CANCEL_WORDS:
            skill = "STOP"
            action = "CANCEL"
            conf = 100
            run_action = False
        else:
            hub_callback = context["hub_callback"] if "hub_callback" in context else None
            if hub_callback:
                try:
                    skill, action = hub_callback.split(".")
                    conf = 100
                    context["hub_callback"] = ""
                    run_action = True
                except:
                    raise RuntimeError("Failed to parse callback")
            else:
                # Brute force check intents cuz why not
                if self.use_keyword_matching:
                    for tag, patterns in self.intents.items():
                        if encoded_command in patterns:
                            skill, action = tag.split("-")
                            conf, run_action = 100, True

                if not run_action:
                    skill, action, conf = self.engine.understand(context)
                    if conf > self.conf_thresh:
                        run_action = True

                if skill in ["NO_COMMAND"] or action in ["NO_ACTION"]:
                    if not run_action:
                        add_false_positive(cleaned_command)
                    else:
                        run_action = False
        
        logger.info(f"Skill: {skill}")
        logger.info(f"Action: {action}")
        logger.info(f"Conf: {conf}")
        context["skill"] = skill
        context["action"] = action
        context["conf"] = conf
        context["run_action"] = run_action

        dt = time.time() - start
        context["time_to_understand"] = dt
        logger.info(f"Time to understand: {dt}")

