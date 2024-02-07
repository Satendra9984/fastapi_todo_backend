from fastapi import FastAPI


app = FastAPI()


BOOKS = [
    {"name": "n1", "author": "a1", "category": "science"},
    {"name": "n3", "author": "a3", "category": "math"},
    {"name": "n2", "author": "a2", "category": "history"},
    {"name": "n3", "author": "a3", "category": "geography"},
    {"name": "n4", "author": "a4", "category": "databases"},
    {"name": "n5", "author": "a5", "category": "math"},

]


@app.get("/firstapi")
async def getBooks() -> dict:
    return {"message": "lets do Fast apis"}


@app.get("/{book_author}")
async def path_parameter_query(book_author: str):
    books = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold():
            books.append(book)
    print(books)        
    return books        


@app.get("/")
async def query_parameter(category:str):
    books = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books.append(book)
    return books    

@app.get("/{author}")
async def path_parameter_query(author: str,category:str):
    books = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold() :
            books.append(book)
        elif category is not None and book.get('category').casefold() == category.casefold():
            books.append(book)

    print(books)        
    return books        




