import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Contact & Donation */}
          <div className="text-center md:text-left">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Contact</h3>
            <div className="space-y-2">
              <a
                href="mailto:info@shortselling.eu"
                className="text-blue-600 hover:text-blue-700 text-sm block"
              >
                info@shortselling.eu
              </a>
            </div>
            
            <div className="mt-6">
              <p className="text-sm text-gray-600 mb-3">
                This website is 100% free. Please consider donating to maintain the project running.
              </p>
              <a
                href="https://buymeacoffee.com/econvibes"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white text-sm font-medium rounded-lg transition-colors"
              >
                ☕ Buy me a coffee
              </a>
            </div>
          </div>

          {/* Legal */}
          <div className="text-center md:text-right">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  to="/terms"
                  className="text-gray-600 hover:text-gray-900 text-sm transition-colors"
                >
                  Terms of Use
                </Link>
              </li>
              <li>
                <Link
                  to="/privacy"
                  className="text-gray-600 hover:text-gray-900 text-sm transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  to="/disclaimer"
                  className="text-gray-600 hover:text-gray-900 text-sm transition-colors"
                >
                  Disclaimer
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="text-sm text-gray-500">
            <p className="mb-2">
              <strong>Disclaimer:</strong> ShortSelling.eu is not affiliated with any European financial regulatory authorities. 
              The information on this website is based on publicly available short-selling registers published by European regulatory authorities.
            </p>
            <p>
              ShortSelling.eu makes no guarantees about the accuracy of the information on this website. 
              For questions and comments, please contact us at{' '}
              <a href="mailto:info@shortselling.eu" className="text-blue-600 hover:text-blue-700">
                info@shortselling.eu
              </a>
            </p>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500 text-center">
            © {new Date().getFullYear()} ShortSelling.eu. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
