from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ThemeCategory(str, Enum):
    """Categories for organizing key insights."""
    MINDSET = "mindset"
    STRATEGY = "strategy"
    EXECUTION = "execution"
    LEADERSHIP = "leadership"
    PERSONAL_DEVELOPMENT = "personal_development"
    SYSTEMS = "systems"
    RELATIONSHIPS = "relationships"
    OTHER = "other"


class MainArgument(BaseModel):
    """The core problem and solution presented in the book."""
    problem_identified: str = Field(
        ..., 
        description="The main problem or challenge the author addresses"
    )
    solution_proposed: str = Field(
        ..., 
        description="The author's proposed solution or approach"
    )
    why_it_matters: str = Field(
        ..., 
        description="Why this problem is significant and worth solving"
    )


class FrameworkComponent(BaseModel):
    """Individual component or step within a framework."""
    name: str = Field(..., description="Name of the component/step")
    description: str = Field(..., description="Detailed explanation")
    example: str = Field(..., description="Practical example demonstrating this component")


class Framework(BaseModel):
    """The main framework, model, or methodology presented."""
    name: str = Field(..., description="Name of the framework/model")
    overview: str = Field(..., description="High-level explanation of the framework")
    components: List[FrameworkComponent] = Field(
        ..., 
        description="Individual steps or components of the framework"
    )
    visual_representation: Optional[str] = Field(
        None, 
        description="Text-based visual or diagram description"
    )


class KeyInsight(BaseModel):
    """A single valuable lesson or insight from the book."""
    title: str = Field(..., description="Short, memorable title for the insight")
    description: str = Field(..., description="Detailed explanation of the insight")
    theme: ThemeCategory = Field(..., description="Category/theme this insight belongs to")
    practical_application: str = Field(
        ..., 
        description="How to apply this insight in real life"
    )
    supporting_quote: Optional[str] = Field(
        None, 
        description="A relevant quote from the book"
    )


class ImplementationStep(BaseModel):
    """A single step in the implementation guide."""
    step_number: int = Field(..., description="Sequential step number")
    title: str = Field(..., description="Brief title of the step")
    description: str = Field(..., description="Detailed instructions")
    time_estimate: Optional[str] = Field(
        None, 
        description="Estimated time to complete (e.g., '1 week', '30 minutes')"
    )
    resources_needed: List[str] = Field(
        default_factory=list, 
        description="Any tools, resources, or materials needed"
    )
    success_criteria: str = Field(
        ..., 
        description="How to know this step is complete"
    )


class ImplementationGuide(BaseModel):
    """Step-by-step guide for applying the book's concepts."""
    overview: str = Field(..., description="Introduction to the implementation approach")
    steps: List[ImplementationStep] = Field(
        ..., 
        description="Sequential steps for implementation"
    )
    common_pitfalls: List[str] = Field(
        ..., 
        description="Common mistakes to avoid during implementation"
    )
    quick_wins: List[str] = Field(
        ..., 
        description="Easy wins readers can achieve quickly"
    )




class OnePageSummary(BaseModel):
    """Condensed one-page reference guide."""
    headline: str = Field(
        ..., 
        description="One-sentence essence of the book"
    )
    core_message: str = Field(
        ..., 
        description="The central message in 2-3 sentences"
    )
    key_principles: List[str] = Field(
        ..., 
        min_items=3,
        max_items=7,
        description="3-7 core principles to remember"
    )
    actionable_takeaways: List[str] = Field(
        ..., 
        min_items=3,
        max_items=5,
        description="3-5 immediate actions readers can take"
    )
    memorable_quote: str = Field(
        ..., 
        description="One powerful quote that captures the book's essence"
    )
    who_should_read: str = Field(
        ..., 
        description="Who would benefit most from this book"
    )
    bottom_line: str = Field(
        ..., 
        description="Final verdict or recommendation"
    )


# class BookMetadata(BaseModel):
#     """Basic information about the book."""
#     title: str = Field(..., description="Book title")
#     author: str = Field(..., description="Author name")
#     publication_year: Optional[int] = Field(None, description="Year published")
#     genre: Optional[str] = Field(None, description="Book genre or category")
#     page_count: Optional[int] = Field(None, description="Number of pages")


class BookAnalysisResponse(BaseModel):
    """The main Pydantic model for the entire book analysis response."""
    
    main_argument: MainArgument = Field(
        ..., 
        description="The core problem and solution presented"
    )
    
    framework: Optional[Framework] = Field(
        None, 
        description="The main framework or methodology (if applicable)"
    )
    
    key_insights: List[KeyInsight] = Field(
        ..., 
        min_items=10,
        max_items=10,
        description="10 most valuable lessons from the book"
    )
    
    implementation_guide: ImplementationGuide = Field(
        ..., 
        description="Step-by-step guide for applying concepts"
    )
    
    one_page_summary: OnePageSummary = Field(
        ..., 
        description="Condensed one-page reference guide"
    )
