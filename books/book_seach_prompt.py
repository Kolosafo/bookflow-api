search_main_prompt = "You're a book search expert. You know how to find books based on book name and author name. Return one item if you know the exact book and a maximum of 5 items if you can't figure out the exact book being searched"

def book_search_prompt (book_title, author=None):
    if author:
        return f"""
            Find the book titled "{book_title}" by {author}.
            """
    else:
        return f"""
            Find the book titled "{book_title}".
            """