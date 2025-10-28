search_main_prompt = "You're a book search expert. If you find that there are many variants of a book with the same title where the author is not passed to specify which one, return the top 5 of them. Otherwise return the exact book."

def book_search_prompt (book_title, author=None):
    if author:
        return f"""
            Find the book titled "{book_title}" by {author}.
            """
    else:
        return f"""
            Find the book titled "{book_title}".
            """