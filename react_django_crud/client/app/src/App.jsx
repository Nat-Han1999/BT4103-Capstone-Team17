import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [books, setBooks] = useState([]); // Empty as API has not been called
  const [title, setTitle] = useState("");
  const [releaseYear, setReleaseYear] = useState(0);

  const [newTitle, setNewTitle] = useState("");

  useEffect(() => {
    fetchBooks(); 
  }, []); // Execute fetchBooks() once, which is when user accesses the page

  const fetchBooks = async() => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/books/");
      const data = await response.json(); // Convert data to JSON
      setBooks(data);
    } catch(err) {
      console.log(error)
    }
  }

  const addBook = async() => {
    const bookData = {
      title,
      release_year: releaseYear,
    };
    // GET request does not need method but the rest do
    try {
    const response = await fetch("http://127.0.0.1:8000/api/books/create/",{
      method: "POST",
      headers: {
        'Content-Type':'application/json', //Type of content you are sending
      },
      body: JSON.stringify(bookData),
    });
    const data = await response.json();
    setBooks((prev)=>[...prev, data]); //Include previously added content
  } catch(err) {
      console.log(err);
    }
  }

  const updateTitle = async(pk, releaseYear) => {
    const bookData = {
      title: newTitle,
      release_year: releaseYear,
    };
    // GET request does not need method but the rest do
    try {
    const response = await fetch(`http://127.0.0.1:8000/api/books/books/${pk}`,{
      method: "PUT",
      headers: {
        'Content-Type':'application/json', //Type of content you are sending
      },
      body: JSON.stringify(bookData),
    });
    const data = await response.json();
    setBooks((prev) => prev.map((book)=> {
      if (book.id == pk) {
        return data;
      } else {
        return book;
      }
    }))
  } catch(err) {
      console.log(err);
    }
  }

  const deleteBook = async(pk) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/books/books/${pk}`,{
        method: "DELETE"
      });
      setBooks((prev)=> prev.filter((book) => book.id !== pk));
    } catch(err) {
      console.log(err);
    }
  }

  return (
    <>
    <h1>Book Website</h1>

    <div>
      <input type ="text" placeholder = "Book Title..." onChange={(e) => setTitle(e.target.value)}/>
      <input type ="number" placeholder = "Release Year..." onChange={(e) => setReleaseYear(e.target.value)}/>
      <button onClick={addBook}>Add Book</button>
    </div>
    {
      books.map((book) => (
        <div>
          <p>Title: {book.tile}</p>
          <p>Release Year: {book.release_year}</p>
          <input type="text" placeholder="New Title..."
          onChange={(e)=> setNewTitle(e.target.value)}/>
          <button onClick={updateTitle(book.id, book.release_year)}>Change Title</button>
          <button onClick={() => deleteBook(book.id)}>Delete</button>
        </div>
      ))
    }
    </>
  )
}

export default App
