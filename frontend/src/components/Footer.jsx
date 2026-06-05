import './Footer.css';
import { Link } from 'react-router-dom';

const navigationLinks = [
    { label: 'Home', to: '/' },
    { label: 'Contact', to: '/contact' },
    { label: 'Discord', to: 'https://discord.gg/9zTNTfVhBD', target: '_blank' },
    { label: 'Privacy Policy', to: '/privacy' },
    { label: 'Terms of Service', to: '/terms' }
];

function Footer() {
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
        </footer>
    )
}

export default Footer; 
