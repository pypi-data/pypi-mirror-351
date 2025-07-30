"""
Images to LLM Pipeline Processor
============================

Complete pipeline for processing image files optimized for LLM consumption.
Supports DSL commands for watermark and resize customization.

DSL Commands:
    [resize_images:50%|800x600] - Image resize specification
    [watermark:auto] - Add watermark to image (auto uses filename)
    [watermark:Custom Text|center|large] - Custom watermark

Usage:
    # Explicit processor access
    result = processors.image_to_llm(attach("image.png"))
    # Like any pipeline and attachment it's ready with adapters
    claude_message_format = result.claude()
"""

from ..core import Attachment
from ..matchers import image_match
from . import processor

@processor(
    match=image_match,
    description="Primary image processor with watermark and resize options"
)
def image_to_llm(att: Attachment) -> Attachment:
    """
    Process image files for LLM consumption.
    
    Supports DSL commands:
    - watermark: auto, or custom text with position/style (defaults to auto if not specified)
    - resize_images: 50%, 800x600 (for resizing)
    
    By default, applies auto watermark to all images for source identification.
    """
    
    # Import namespaces properly to get VerbFunction wrappers
    from .. import load, modify, present, refine
    
    # Enhanced pipeline with URL support and image control
    return (att 
           | load.url_to_file          # Handle URLs first - download if needed
           | load.image_to_pil         # Then load as PIL Image
           | modify.watermark          # Apply auto watermark by default
           | present.images + present.metadata
           | refine.resize_images | refine.add_headers)
