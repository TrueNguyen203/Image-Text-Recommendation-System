import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import Product from '../components/Product';

export default function Preference() {
  const location = useLocation();
  const history = location.state?.history;
  const [recImage, setRecImage] = useState([]);
  const [recText, setRecText] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const APIURL = "http://localhost:8000/preference";

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const response = await axios.post(APIURL, null, {
          params: { sku: parseInt(history) },
        });
        const data = response.data;
        setRecImage(data.image || []);
        setRecText(data.text || []);
      } catch (e) {
        console.error(e);
        setError('Error fetching recommendations');
      } finally {
        setLoading(false);
      }
    };

    if (history) {
      fetchRecommendations();
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) return <div className="bg-white pt-20 text-center py-20">Loading...</div>;
  if (error) return <div className="bg-white pt-20 text-center py-20 text-red-600">{error}</div>;

  return (
    <div className="bg-white mt-20">
      <div className="px-6 py-12 max-w-8xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">Preference Recommendations</h1>
        
        {recImage.length > 0 && (
          <div className="mb-12">
            <h2 className="w-full bg-gray-100 text-2xl font-bold mb-6 p-1.5">Based on Image Similarity</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {recImage.map((product) => (
                <Product key={product.sku || Math.random()} {...product} />
              ))}
            </div>
          </div>
        )}

        {recText.length > 0 && (
          <div className="mb-12">
            <h2 className="w-full bg-gray-100 text-2xl font-bold mb-6 p-1.5">Based on Text Similarity</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {recText.map((product) => (
                <Product key={product.sku || Math.random()} {...product} />
              ))}
            </div>
          </div>
        )}

        {recImage.length === 0 && recText.length === 0 && (
          <div className="text-center text-gray-500">No recommendations found.</div>
        )}
      </div>
    </div>
  );
}