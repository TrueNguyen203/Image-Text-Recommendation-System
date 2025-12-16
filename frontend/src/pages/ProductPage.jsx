import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

export default function ProductPage() {
    const { sku } = useParams();
    const APIURL = "http://localhost:8000/";
    const [selectedImage, setSelectedImage] = useState(0);
    const [selectedSize, setSelectedSize] = useState('');
    const [expandedSection, setExpandedSection] = useState(null);
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchProduct = async (sku) => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(APIURL, {
                params: {
                    sku: sku,
                },
            });
            const data = response.data;
            
            if (data.error) {
                setError(data.error);
                setProduct(null);
            } else {
                setProduct(data);
            }
        } catch (e) {
            console.error(e);
            const errorMessage = e.response?.data?.error || e.message;
            setError(errorMessage);
            setProduct(null);
        } finally {
            setLoading(false);
        }
    };
    
useEffect(() => {
        fetchProduct(sku);
    }, []);

    // const product = {
    //     name: 'adidas Originals Paris illustration graphic t-shirt in white',
    //     price: 48.00,
    //     color: 'wonder white',
    //     brand: 'New Look',
    //     sku: 1,
    //     images: ['https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-4?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-1-neutral?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-2?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-3?$n_1920w$&wid=1926&fit=constrain', 'https://images.asos-media.com/products/new-look-trench-coat-in-camel/204351106-4?$n_1920w$&wid=1926&fit=constrain'],
    //     in_stock_size: ['1', '2', '3', '4', '5'],
    //     description: [{'Product Details': 'Coats & Jackets by New LookLow-key layeringNotch collarButton placketTie waistRegular fitProduct Code: 126704571'}, {'Brand': 'Since setting up shop in the 60s, New Look has become a high-street classic known for creating universally loved, wardrobe-ready collections. Shop the New Look at ASOS edit, featuring everything from chic LBDs and printed dresses to all-important accessories and figure-flattering jeans (if you re anything like us, you re always on the hunt for those). While you re there, check out the label s cute-yet-classy tops and blouses for your next jeans and a nice top day.'}, {'Size & Fit': "Model wears: UK 8/ EU 36/ US 4Model's height: 170 cm/5'7 "}, {'Look After Me': 'Machine wash according to instructions on care label'}, {'About Me': 'Stretch, plain-woven fabricMain: 55% Polyester, 45% Elastomultiester.'}],
    // };
    
    if (loading) {
        return <div className="bg-white pt-20 text-center py-20">Loading...</div>;
    }

    if (error) {
        return <div className="bg-white pt-20 text-center py-20 text-red-600">Error: {error}</div>;
    }

    if (!product) {
        return <div className="bg-white pt-20 text-center py-20">Product not found</div>;
    }
    
    console.log(product)

    const details = product.description.map(item => {
        const [[title, value]] = Object.entries(item);
        const formattedContent = value
        .replace(/([a-z])([A-Z])/g, '$1. $2')
        .replace(/\s+/g, ' ')
        .trim();
        return {
        title,
        content: formattedContent,
        }
    });

    const toggleSection = (section) => {
        setExpandedSection(expandedSection === section ? null : section);
    };

    return (
        <div className="bg-white pt-20">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left - Images */}
                    <div className="flex gap-4">
                        {/* Thumbnail Images */}
                        <div className="flex flex-col gap-3 w-20">
                            {product.images.map((image, index) => (
                                <button
                                    key={index}
                                    onClick={() => setSelectedImage(index)}
                                    className={`w-20 h-24 border-2 overflow-hidden ${selectedImage === index ? 'border-gray-800' : 'border-gray-200'}`}
                                >
                                    <img src={image} alt={`View ${index + 1}`} className="w-full h-full object-cover" />
                                </button>
                            ))}
                        </div>

                        {/* Main Image */}
                        <div className="flex-1 relative">
                            <img
                                src={product.images[selectedImage]}
                                alt={product.name}
                                className="w-full h-auto object-cover"
                            />
                            {/* Model Info */}
                            <div className="mt-2 text-center text-md text-gray-600">
                                {details[2].content}
                            </div>
                        </div>
                    </div>

                    {/* Right - Product Info */}
                    <div className="flex flex-col gap-6 px-1">
                        {/* Title */}
                        <div>
                            <h1 className="text-2xl font-medium text-gray-900">
                                {product.name}
                            </h1>
                        </div>

                        {/* Price */}
                        <div>
                            <p className="text-3xl font-bold text-gray-900">
                                €{product.price.toFixed(2)}
                            </p>
                        </div>

                        {/* Color */}
                        <div>
                            <p className="text-lg font-medium text-gray-900">
                                COLOUR: <span className="text-gray-600">{product.color}</span>
                            </p>
                        </div>

                        {/* Size Selection */}
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <label className="text-sm font-medium text-gray-900">SIZE:</label>
                                <a href="#" className="text-sm font-medium text-gray-900 underline">Size Guide</a>
                            </div>
                            <select
                                value={selectedSize}
                                onChange={(e) => setSelectedSize(e.target.value)}
                                className="w-full border border-gray-300 rounded px-4 py-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-800"
                            >
                                <option value="">Please select</option>
                                {product.in_stock_size.map((size) => (
                                    <option key={size} value={size}>{'UK ' + size}</option>
                                ))}
                            </select>
                        </div>

                        {/* Add to Bag */}
                        <div className="flex gap-4">
                            <button className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded transition cursor-pointer">
                                ADD TO BAG
                            </button>
                            <button className="border border-gray-300 px-6 py-3 rounded hover:bg-gray-50 transition cursor-pointer">
                                ♥
                            </button>
                        </div>

                        {/* Delivery Info */}
                        <div className="border-t border-gray-200 pt-4">
                            <p className="text-sm text-gray-600 mb-2">
                                🚚 Free delivery on qualifying orders.
                            </p>
                            <a href="#" className="text-sm font-medium text-gray-900 underline">
                                View our Delivery & Returns Policy
                            </a>
                            <p className="text-xs text-gray-500 mt-2">
                                This product has shipping restrictions.
                            </p>
                        </div>

                        {/* Expandable Sections */}
                        <div className="border-t border-gray-200 pt-4 space-y-0">
                            {details.map((detail, index) => (
                                <div key={index}>
                                    <button
                                        onClick={() => toggleSection(detail.title)}
                                        className="w-full flex justify-between items-center py-3 border-b border-gray-200 hover:bg-gray-50 transition px-1"
                                    >
                                        <span className="text-lg font-medium text-gray-900">{detail.title}</span>
                                        <span className="text-lg cursor-pointer">
                                            {expandedSection === detail.title ? '−' : '+'}
                                        </span>
                                    </button>

                                    {/* Expanded Content */}
                                    {expandedSection === detail.title && (
                                        <div className="bg-gray-50 p-4 border-b border-gray-200">
                                            <p className="text-md text-gray-700 whitespace-pre-wrap">
                                                {detail.content}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}