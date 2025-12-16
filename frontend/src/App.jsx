import { useState, useEffect } from 'react';
//Pages
import Home from './pages/Home'
import Recomender from './pages/Recommender'
import ProductPage from './pages/ProductPage'
import Login from './pages/Login'
import Register from './pages/Register'
import Preference from './pages/Preference';

//Components
import NavBar from './components/NavBar'
import Footer from './components/Footer';

//Sytle
import './App.css'
import './index.css'

// Routes
import {Routes, Route} from 'react-router-dom'

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('accessToken');
    setUser(null);
  };

  return (
    <div>
      <NavBar user={user} onLogout={handleLogout} />
      <main className='main-content'>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/recommender' element={<Recomender />} />
          <Route path='/preference' element={<Preference />} />
          <Route path='/product/:sku' element={<ProductPage />} />
          <Route path='/login' element={<Login setUser={setUser} />} />
          <Route path='/register' element={<Register />} />
        </Routes>
      <Footer />
      </main>
    </div>
  )
}

export default App