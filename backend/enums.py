import enum

class PipelineStages(enum.Enum):
    Transcribe = 'transcribe'
    Understand = 'understand'
    Skillset = 'skillset'
    Synthesize = 'synthesize'