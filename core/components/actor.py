import time
import logging
logger = logging.getLogger("components.actor")

from core.schemas import Context
from core.utils.nlp.formatting import format_sentences

class Actor:
    def __init__(self, ova: "OpenVoiceAssistant"):
        self.ova = ova

    def process_response(self, text: str):
        if not text:
            return text
        text = text.strip()
        text = ". ".join([sentence.strip().capitalize() for sentence in text.split(".")])
        text = text.replace(" i ", " I ")
        text = text.strip()
        if text[0] == "i": text[0] = "I"
        if text[-1] not in  [".", "!", "?" "%"]: text += "."
        return text

    def run_stage(self, context: Context):
        logger.info("Action Stage")
        start = time.time()

        skill = context["skill"]
        action = context["action"]
        run_action = context["run_action"]

        if not run_action:
            context["response"] = ""
        else:
            if self.ova.skill_manager.skill_imported(skill):
                try:
                    getattr(self.ova.skill_manager.get_skill_module(skill), action)(context)
                except Exception as e:
                    context["response"] = f"Sorry. While executing that action, I encountered the following problem. {str(e)}"
            else:
                context["response"] = "Skill is not imported."

        if "response" not in context:
            if "synth_response" in context:
                context["response"] = context["synth_response"]
            else:
                context["response"] = ""
        if "synth_response" not in context:
            context["synth_response"] = context["response"]

        context["response"] = format_sentences(context["response"])
        context["synth_response"] = format_sentences(context["synth_response"])

        dt = time.time() - start
        logger.info(f"Time to run action: {dt}")
        context["time_to_action"] = dt