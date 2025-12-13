import {useNavigate} from 'react-router-dom';


export default function Product(props) {
    const navigate = useNavigate();

    return (
        <div 
        key={props.sku}
        className="bg-white cursor-pointer hover:shadow-lg transition"
        onClick={() => {
            navigate(`/product/${props.sku}`)
        }}>
            {/* Product Image */}
            <div className="w-full bg-gray-200 overflow-hidden">
                <img
                    src={props.images[0]}
                    alt={props.name}
                    className="w-full object-cover hover:scale-105 transition duration-300"
                />
            </div>
            <div className="p-4">
                <h2 className="text-lg font-medium text-gray-800 line-clamp-2">
                    {props.name}
                </h2>
                <p className="text-xl font-bold text-gray-900 mt-2">
                    <span>€</span>
                    {props.price}
                </p>
            </div>
        </div>
    )
}