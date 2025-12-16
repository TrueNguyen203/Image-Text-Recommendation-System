import { useState } from 'react';
import axios from 'axios';
import Product from '../components/Product';

export default function Recommender() {
  const [queryText, setQueryText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedBrand, setSelectedBrand] = useState('All');
  const [selectedColor, setSelectedColor] = useState('All');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const brands = ['All','Stradivarius', 'Asos Petite', 'Topshop', 'Bershka',
    'Asos Curve', 'Collusion', 'Miss Selfridge', 'New Look', 'Asyou',
    'River Island', 'Asos Tall', 'Adidas Originals', 'Asos Edition', 'Monki'];
  const colors = ['All', 'WHITE', 'PINK', 'GREEN', 'BLUE', 'BROWN', 'RED', 'KHAKI', 'CREAME'];

  const APIURL = "http://localhost:8000";

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setProducts([]);

    const formData = new FormData();
    if (selectedFile) {
      formData.append('file', selectedFile);
    }
    if (queryText) {
      formData.append('query_text', queryText);
    }
    
    formData.append('brand', selectedBrand === 'All' ? '' : selectedBrand);
    formData.append('color', selectedColor === 'All' ? '' : selectedColor);

    try {
      const response = await axios.post(`${APIURL}/search`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setProducts(response.data);
    } catch (err) {
      console.error(err);
      setError('Error fetching recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white mt-20">
      <div className="px-6 py-12 max-w-8xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">Recommender Search Engine</h1>
        
        <form onSubmit={handleSearch} className="max-w-5xl min-w-2xl mx-auto space-y-6 bg-gray-100 p-8 rounded-lg shadow-sm">
          <div>
            <label className="block text-md font-medium text-gray-700 mb-1">Search Query</label>
            <input
              type="text"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Enter text..."
            />
          </div>

          <div>
            <label className="block text-md font-medium text-gray-700 mb-1">Upload Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-md font-medium text-gray-700 mb-1">Brand</label>
              <select
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {brands.map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-md font-medium text-gray-700 mb-1">Color</label>
              <select
                value={selectedColor}
                onChange={(e) => setSelectedColor(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {colors.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && (
          <div className="mt-8 text-center text-red-600">
            {error}
          </div>
        )}

        {products.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-6">Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {products.map((product) => (
                <Product key={product.sku || Math.random()} {...product} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}