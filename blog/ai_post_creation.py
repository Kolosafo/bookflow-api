import json
from datetime import datetime
from pathlib import Path
from google.genai import types
from books.AI_MODELS import GEMINI_CLIENT

# Initialize Gemini client

# Pydantic-like schema for structured output
BlogStructureSchema = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "SEO-optimized blog title"},
        "meta_description": {"type": "string", "description": "Meta description for SEO (150-160 chars)"},
        "slug": {"type": "string", "description": "URL-friendly slug"},
        "should_promote_bookflow": {"type": "boolean", "description": "Whether to include BookFlow promotion"},
        "bookflow_placement": {"type": "string", "enum": ["none", "early", "middle", "end"], "description": "Where to place BookFlow CTA"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "content": {"type": "string", "description": "Markdown formatted content"},
                    "needs_image": {"type": "boolean"},
                    "image_prompt": {"type": "string", "description": "Prompt for image generation if needed"}
                }
            }
        },
        "cover_image_prompt": {"type": "string", "description": "Prompt for cover image"},
        "keywords": {"type": "array", "items": {"type": "string"}, "description": "SEO keywords"},
        "reading_time": {"type": "integer", "description": "Estimated reading time in minutes"}
    },
    "required": ["title", "meta_description", "slug", "should_promote_bookflow", "sections", "cover_image_prompt", "keywords"]
}

def create_blog_generation_prompt(keyword):
    """Create the main prompt for blog generation"""
    return f"""You are an expert blog writer creating content for BookFlow, an app that helps users absorb knowledge faster with AI-generated book summaries, key insights, and practical takeaways.

KEYWORD: {keyword}

YOUR TASK:
1. Create a comprehensive, SEO-optimized blog post about "{keyword}"
2. Write in a conversational, human tone - avoid robotic or overly formal language
3. Use natural transitions and varied sentence structures
4. Include personal touches like "we've found", "in our experience", etc.
5. Determine if BookFlow is relevant to this topic:
   - PROMOTE BookFlow if: topic relates to learning, non-fiction books, productivity, self-improvement, business books, educational content, skill development
   - DON'T PROMOTE BookFlow if: pure fiction/fantasy, entertainment novels, poetry, children's books, or topics unrelated to knowledge absorption
6. Structure the post with 5-7 sections, each 200-400 words
7. Identify 2-3 sections that would benefit from illustrative images
8. Create an engaging cover image prompt

SEO REQUIREMENTS:
- Primary keyword "{keyword}" should appear naturally 5-8 times
- Include related long-tail keywords
- Use H2 and H3 headings strategically
- Write compelling meta description with keyword

BOOKFLOW INTEGRATION (if relevant):
- Introduce BookFlow naturally within the content, not as a forced ad
- Explain how it specifically helps with the blog topic
- Place CTA strategically: early for high-intent topics, middle/end for informational content
- Example: "If you're interested in diving deeper into [topic], BookFlow can help you extract the key insights from the best books on [subject] in minutes..."

OUTPUT FORMAT:
Return a structured JSON with title, sections, image requirements, and BookFlow strategy."""

def generate_blog_structure(keyword):
    """Generate the blog structure using Gemini"""
    conversation = [
        {
            "role": "user",
            "parts": [{"text": create_blog_generation_prompt(keyword)}]
        }
    ]
    
    response = GEMINI_CLIENT.models.generate_content(
        model="gemini-2.0-flash-exp",  # Using flash for cost-effectiveness
        contents=conversation,
        config={
            "response_mime_type": "application/json",
            "response_schema": BlogStructureSchema,
            "temperature": 0.8,  # Higher creativity for natural writing
        },
    )
    
    return json.loads(response.text)

def generate_cover_image(prompt, keyword):
    """Generate cover image for the blog post"""
    enhanced_prompt = f"{prompt}. Professional blog cover image style, high quality, engaging, relevant to '{keyword}'. 16:9 aspect ratio."
    
    response = GEMINI_CLIENT.models.generate_image(
        model="imagen-3.0-fast-generate-001",  # Using fast model for cost-effectiveness
        prompt=enhanced_prompt,
        config=types.GenerateImageConfig(
            number_of_images=1,
            include_rai_reasoning=False,  # Disable to reduce cost
            output_mime_type="image/jpeg",
        ),
    )
    
    return response.generated_images[0].image.image_bytes

def generate_section_image(prompt, section_heading):
    """Generate image for a blog section"""
    enhanced_prompt = f"{prompt}. Illustrative image for blog section about '{section_heading}'. Clear, professional, informative style."
    
    response = GEMINI_CLIENT.models.generate_image(
        model="imagen-3.0-fast-generate-001",
        prompt=enhanced_prompt,
        config=types.GenerateImageConfig(
            number_of_images=1,
            include_rai_reasoning=False,
            output_mime_type="image/jpeg",
        ),
    )
    
    return response.generated_images[0].image.image_bytes

def create_bookflow_cta(placement="middle"):
    """Create BookFlow call-to-action section"""
    ctas = {
        "early": """
## Absorb Knowledge Faster with BookFlow

Before we dive deeper, here's something that can accelerate your learning: **BookFlow** transforms dense books into actionable insights you can absorb in minutes. Whether you're exploring this topic or expanding into related areas, our AI-generated summaries help you extract key takeaways without spending hours reading.

[**Download BookFlow**](#) and start learning smarter today.

---
""",
        "middle": """
---

### 📚 Level Up Your Learning with BookFlow

Want to dive deeper into these concepts? **BookFlow** helps you absorb knowledge from the world's best books faster. Get AI-generated summaries, key insights, and practical takeaways that you can apply immediately.

Perfect for busy learners who want to stay ahead without the time commitment.

[**Try BookFlow Free**](#)

---
""",
        "end": """
---

## Continue Your Learning Journey

If you found this post valuable, imagine having access to insights from thousands of books at your fingertips. **BookFlow** makes it possible.

Our app delivers:
- ⚡ AI-generated summaries of bestselling books
- 🎯 Key insights you can apply today
- 📖 Practical takeaways for real-world use

Stop letting great books sit on your shelf unread. **[Download BookFlow](#)** and absorb knowledge faster.
"""
    }
    return ctas.get(placement, ctas["middle"])

def compile_blog_markdown(blog_data, keyword, image_paths):
    """Compile the final blog post in markdown format"""
    markdown = f"""---
title: "{blog_data['title']}"
description: "{blog_data['meta_description']}"
slug: {blog_data['slug']}
keywords: {', '.join(blog_data['keywords'])}
date: {datetime.now().strftime('%Y-%m-%d')}
reading_time: {blog_data.get('reading_time', 5)} min
cover_image: {image_paths['cover']}
---

# {blog_data['title']}

![{blog_data['title']}]({image_paths['cover']})

"""
    
    bookflow_inserted = False
    section_image_idx = 0
    
    for idx, section in enumerate(blog_data['sections']):
        # Add section heading
        markdown += f"\n## {section['heading']}\n\n"
        
        # Add section content
        markdown += f"{section['content']}\n\n"
        
        # Add section image if needed
        if section.get('needs_image') and section_image_idx < len(image_paths['sections']):
            image_path = image_paths['sections'][section_image_idx]
            markdown += f"![{section['heading']}]({image_path})\n\n"
            section_image_idx += 1
        
        # Insert BookFlow CTA at appropriate position
        if blog_data['should_promote_bookflow'] and not bookflow_inserted:
            placement = blog_data.get('bookflow_placement', 'middle')
            
            if placement == 'early' and idx == 1:
                markdown += create_bookflow_cta('early')
                bookflow_inserted = True
            elif placement == 'middle' and idx == len(blog_data['sections']) // 2:
                markdown += create_bookflow_cta('middle')
                bookflow_inserted = True
    
    # Add end CTA if not inserted yet and should promote
    if blog_data['should_promote_bookflow'] and not bookflow_inserted:
        markdown += create_bookflow_cta('end')
    
    # Add conclusion
    markdown += f"\n---\n\n*Keywords: {', '.join(blog_data['keywords'])}*\n"
    
    return markdown

def generate_blog_post(keyword, output_dir="blog_posts"):
    """Main function to generate complete blog post"""
    print(f"🚀 Generating blog post for keyword: {keyword}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate blog structure
    print("📝 Creating blog structure...")
    blog_data = generate_blog_structure(keyword)
    
    # Create subdirectory for this post
    post_slug = blog_data['slug']
    post_dir = output_path / post_slug
    post_dir.mkdir(exist_ok=True)
    
    # Generate cover image
    print("🖼️  Generating cover image...")
    cover_image_bytes = generate_cover_image(blog_data['cover_image_prompt'], keyword)
    cover_image_path = post_dir / "cover.jpg"
    with open(cover_image_path, "wb") as f:
        f.write(cover_image_bytes)
    
    # Generate section images
    image_paths = {
        'cover': './cover.jpg',
        'sections': []
    }
    
    section_images_needed = [s for s in blog_data['sections'] if s.get('needs_image')]
    print(f"🎨 Generating {len(section_images_needed)} section images...")
    
    for idx, section in enumerate(section_images_needed):
        if section.get('image_prompt'):
            img_bytes = generate_section_image(section['image_prompt'], section['heading'])
            img_path = post_dir / f"section_{idx+1}.jpg"
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            image_paths['sections'].append(f"./section_{idx+1}.jpg")
    
    # Compile markdown
    print("📄 Compiling markdown...")
    markdown_content = compile_blog_markdown(blog_data, keyword, image_paths)
    
    # Save markdown file
    markdown_path = post_dir / f"{post_slug}.md"
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    # Save metadata
    metadata_path = post_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(blog_data, f, indent=2)
    
    print(f"✅ Blog post generated successfully!")
    print(f"📁 Location: {post_dir}")
    print(f"📊 Stats:")
    # print(f"   - Sections: {len(blog_data['sections'])}")
    # print(f"   - Images: {len(image_paths['sections']) + 1}")
    # print(f"   - BookFlow promotion: {'Yes' if blog_data['should_promote_bookflow'] else 'No'}")
    # print(f"   - Reading time: ~{blog_data.get('reading_time', 5)} minutes")
    
    return {
        'post_dir': str(post_dir),
        'markdown_path': str(markdown_path),
        'blog_data': blog_data
    }

# # Example usage
# if __name__ == "__main__":
#     # Example keywords
#     keywords = [
#         "productivity tips for entrepreneurs",
#         "best fantasy books 2024",
#         "how to learn faster",
#     ]
    
#     # Generate blog for the first keyword
#     result = generate_blog_post(keywords[0])
#     print(f"\n🎉 Done! Check out your blog post at: {result['markdown_path']}")