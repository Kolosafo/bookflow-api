main_prompt = "You're a book expert. You know how to analyze books, find their keypoints, generate key insights and implementation guides."

def keypoints_prompt (book_title, author):
    return f"""
        Analyze "{book_title}" by {author} focusing on:

        1. **Main Argument**: What problem does the author identify and what solution do they propose?

        2. **Framework/Model**: If the book presents a framework, model, or methodology, explain it clearly with examples.

        3. **Key Insights** (10 points): Extract the most valuable lessons, organized by theme.

        4. **Implementation Guide**: How can readers apply these concepts? Provide a step-by-step approach.

        5. **Evidence & Case Studies**: What research, data, or examples does the author use to support their claims?

        6. **Controversies & Criticisms**: What are potential counterarguments or limitations?

        7. **One-Page Summary**: Distill the entire book into a single-page reference guide.

        """