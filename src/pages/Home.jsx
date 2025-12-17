import { useState, useEffect } from 'react';
import axios from 'axios';
import Product from '../components/Product';


export default function Home() {
  const [productsByBrand, setProductsByBrand] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const brands = ['Stradivarius', 'Asos Petite', 'Topshop', 'Bershka',
    'Asos Curve', 'Collusion', 'Miss Selfridge', 'New Look', 'Asyou',
    'River Island', 'Asos Tall', 'Adidas Originals', 'Asos Edition', 'Monki'];

  const APIURL = "http://localhost:8000";

  useEffect(() => {
    const fetchProductsByBrands = async () => {
      setLoading(true);
      setError(null);
      try {
        const requests = brands.map(brand =>
          axios.post(`${APIURL}/products-by-brand`, { brand })
        );
        const responses = await Promise.all(requests);
        const allProducts = responses.flatMap(response => response.data);
        
        const groupedProducts = allProducts.reduce((acc, product) => {
          const brandName = product.brand;
          if (!acc[brandName]) {
            acc[brandName] = [];
          }
          acc[brandName].push(product);
          return acc;
        }, {});

        setProductsByBrand(groupedProducts);
      } catch (e) {
        console.error(e);
        const errorMessage = e.response?.data?.error || e.message;
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchProductsByBrands();
  }, []);

  if (loading) {
    return <div className="bg-white pt-20 text-center py-20">Loading products...</div>;
  }

  if (error) {
    return <div className="bg-white pt-20 text-center py-20 text-red-600">Error: {error}</div>;
  }

  return (
    <div className="bg-white mt-20">
      {/* Products Grid */}
      <div className="px-6 py-12 max-w-7xl mx-auto">
        {Object.entries(productsByBrand).map(([brand, brandProducts]) => (
          <div key={brand} className="mb-12">
            <h2 className="w-full bg-gray-100 text-3xl text-center font-bold tracking-tight text-gray-900 mb-4 py-4 px-2">{brand}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {brandProducts.map((product) => (
                <Product key={product.sku} {...product} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}