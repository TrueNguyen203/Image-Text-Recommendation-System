import {Link} from 'react-router-dom';
import asosLogo from '../assets/asosLogo.svg';

export default function NavBar() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#2C2C2C] flex items-center justify-between xl:px-32 md:px-16 sm: px-8 py-4 gap-8 h-20">
            {/* Logo */}
            <Link to="/" className="shrink-0">
                <img
                    className="w-20 h-6 brightness-0 invert"
                    src={asosLogo}
                    alt="ASOS Logo"
                />  
            </Link>

            {/* Right Icons */}
            <div className="flex gap-6 items-center">
                <Link to="/recommender" className="text-white hover:text-gray-300 hover:underline hover:decoration-white transition">
                    <p className='text-lg font-medium'>
                        Recommender System
                    </p>
                </Link>
                <button className="text-white hover:text-gray-300 transition cursor-pointer">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4l1-12z" />
                    </svg>
                </button>
            </div>
        </nav>
    )
}