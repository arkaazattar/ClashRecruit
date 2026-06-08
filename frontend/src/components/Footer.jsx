import './Footer.css';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import sitCat from '../assets/Sit_Cat.png';
import sleepCat from '../assets/Sleep_Cat.png';

const navigationLinks = [
    { label: 'Home', to: '/' },
    { label: 'Contact', to: '/contact' },
    { label: 'Discord', to: 'https://discord.gg/9zTNTfVhBD', target: '_blank' },
    { label: 'Privacy Policy', to: '/privacy' },
    { label: 'Terms of Service', to: '/terms' }
];

function Footer() {
    const [catSleeping, setCatSleeping] = useState(false);
    const footerCat = catSleeping ? sleepCat : sitCat;

    return (
        <footer className="footer">
            <nav className="footer__nav" aria-label="Footer navigation">
                {navigationLinks.map((link) => (
                    <Link
                        key={link.to}
                        to={link.to}
                        className="footer__link"
                        target={link.target}
                        rel={link.target === '_blank' ? 'noopener noreferrer' : undefined}
                    >
                        {link.label}
                    </Link>
                ))}
            </nav>

            <section className="footer__legal" aria-label="Legal information">
                <p className="footer__copyright">© 2026 ClashRecruit</p>
                <label className="footer__fan-policy">
                    This material is unofficial and is not endorsed by Supercell.
                    For more information see Supercell's Fan Content Policy:{' '}
                    <a target="_blank" href="https://supercell.com/en/fan-content-policy/" rel="noopener noreferrer">www.supercell.com/fan-content-policy</a>.
                </label>
            </section>

            <button
                type="button"
                className="footer__cat"
                onClick={() => setCatSleeping(true)}
                aria-label="Put footer cat to sleep"
            >
                <img src={footerCat} alt="" className="footer__cat-image" aria-hidden="true" />
            </button>
        </footer>
    )
}

export default Footer; 
