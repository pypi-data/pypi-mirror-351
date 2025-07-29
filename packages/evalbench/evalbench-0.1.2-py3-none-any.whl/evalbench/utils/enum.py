from enum import Enum

class ScoredEnum(Enum):
    def __init__(self, score, description):
        self.score = score
        self.description = description

    @classmethod
    def from_score(cls, score: float):
        for member in cls:
            if member.score == score:
                return member
        return None

class Relevance(ScoredEnum):
    IRRELEVANT = (1, 'Completely irrelevant')
    SLIGHTLY_RELATED = (2, 'Weakly related, mostly off-topic')
    SOMEWHAT_RELEVANT = (3, 'Partially relevant, some connection')
    MOSTLY_RELEVANT = (4, 'Mostly relevant, minor issues')
    HIGHLY_RELEVANT = (5, 'Highly relevant')

class AnswerHelpfulness(ScoredEnum):
    IRRELEVANT = (1, 'Unhelpful or irrelevant')
    SLIGHTLY_HELPFUL = (2, 'Slightly helpful, mostly vague')
    SOMEWHAT_HELPFUL = (3, 'Somewhat helpful, partially answers')
    MOSTLY_HELPFUL = (4, 'Mostly helpful, minor issues')
    HIGHLY_HELPFUL = (5, 'Very helpful, clear and complete')

class Groundedness(ScoredEnum):
    NOT_GROUNDED = (1, 'Unrelated or contradicts context')
    PARTIALLY_GROUNDED = (2, 'Uses some context, but incomplete')
    FULLY_GROUNDED = (3, 'Completely supported by context')

class Conciseness(ScoredEnum):
    TOO_VERBOSE = (1, 'Repetitive or long')
    SOMEWHAT_CONCISE = (2, 'Communicates key ideas but could be shorter')
    VERY_CONCISE = (3, 'Clear and avoids unnecessary detail')

class Coherence(ScoredEnum):
    INCOHERENT = (1, 'Hard to follow or disjointed')
    SOMEWHAT_COHERENT = (2, 'Mostly makes sense but has minor gaps')
    VERY_COHERENT = (3, 'Logical and well-connected')