"""Code that handles the InformationExtractionAgent"""

class BaseExtractorAgent:
    """Core logic that other agents of this type extend from for extracting information."""
    pass

class NamedEntityExtractorAgent(BaseExtractorAgent):
    """Class that extends BaseExtractorAgent and performs entity extraction techniques on information"""
    pass

class NoteExtractorAgent(BaseExtractorAgent):
    """Class that extends BaseExtractorAgent and extracts information that is given in text that might be notes to keep in longterm storage"""
    pass

class InventoryExtractorAgent(BaseExtractorAgent):
    pass