//Pages
import Home from './pages/Home'
import Recomender from './pages/Recommender'
import ProductPage from './pages/ProductPage'

//Components
import NavBar from './components/NavBar'

//Sytle
import './App.css'
import './index.css'

// Routes
import {Routes, Route} from 'react-router-dom'

function App() {
  return (
    <div>
      <NavBar />
      <main className='main-content'>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/recommender' element={<Recomender />} />
          <Route path='/product/:sku' element={<ProductPage />} />'
        </Routes>
      </main>
    </div>
  )
}

export default App