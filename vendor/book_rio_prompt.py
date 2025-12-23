BOOK_ROI_PROMPT = """You are an expert at matching books to readers' needs and calculating the potential value of reading a specific book.

Given:
- Book: "{book_title}" by {author}
- Reader's Goal: "{reader_goal}"
- Reader's Challenge: "{reader_challenge}"
- Available Time: "{available_time}"

Analyze whether this book is a good fit for this specific reader and calculate their potential "Reading ROI".

Provide:
1. **ROI Score** (0-100): How valuable this book will be for THIS reader's specific situation
   - 80-100: Highly recommended, directly addresses their needs
   - 60-79: Good fit, relevant with some tangential benefits
   - 40-59: Moderate fit, some applicable insights
   - 20-39: Limited fit, better alternatives exist
   - 0-19: Poor fit, won't address their needs

2. **Match Reasoning** (2-3 sentences): Explain WHY this score, connecting the book's content to their specific goal and challenge

3. **Relevant Takeaways** (3-4 bullet points): What will THIS reader specifically gain that relates to their situation

4. **Time Analysis** (1-2 sentences): Estimated reading time and whether the time investment is worth it for their situation

Be honest - if the book isn't a great fit, say so and briefly mention what type of book would be better.

Return response in JSON format:
{{
  "roi_score": number (0-100),
  "match_reasoning": "string",
  "relevant_takeaways": ["takeaway 1", "takeaway 2", ...],
  "time_analysis": "string",
  "estimated_reading_hours": number,
  "recommendation": "highly_recommended" | "recommended" | "moderately_recommended" | "not_recommended"
}}
"""




def book_rio_action_prompt (book_title, author=None):
    return f"""
        match the user book titled "{book_title}" by {author}, based on the informatio provided.
        """

            
