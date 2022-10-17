import enum

class PipelineStages(enum.Enum):
    Transcribe = 'transcribe'
    Understand = 'understand'
    Skillset = 'skillset'
    Synthesize = 'synthesize'

class Components(enum.Enum):
    Transcriber = 'transcriber'
    Understander = 'understander'
    Skillset = 'skillset'
    Synthesizer = 'synthesizer'

pipeline_to_component = {
    PipelineStages.Transcribe: Components.Transcriber,
    PipelineStages.Understand: Components.Understander,
    PipelineStages.Skillset: Components.Skillset,
    PipelineStages.Synthesize: Components.Synthesizer,
}