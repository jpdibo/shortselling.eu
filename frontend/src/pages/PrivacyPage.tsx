import React from 'react';

const PrivacyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Privacy Policy</h1>
      
      <div className="prose prose-lg max-w-none">
        <p className="text-gray-600 mb-4">
          <strong>Last updated:</strong> {new Date().toLocaleDateString()}
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Information We Collect</h2>
        <p className="text-gray-700 mb-4">
          We collect information you provide directly to us, such as when you subscribe to our email updates. This may include your name and email address.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. How We Use Your Information</h2>
        <p className="text-gray-700 mb-4">
          We use the information we collect to provide, maintain, and improve our services, to send you updates about short-selling positions, and to communicate with you.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. Information Sharing</h2>
        <p className="text-gray-700 mb-4">
          We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this privacy policy.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Data Security</h2>
        <p className="text-gray-700 mb-4">
          We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Cookies and Analytics</h2>
        <p className="text-gray-700 mb-4">
          We use Google Analytics to understand how visitors interact with our website. This service may use cookies and similar technologies to collect information about your use of our website.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Your Rights</h2>
        <p className="text-gray-700 mb-4">
          You have the right to access, update, or delete your personal information. You can also unsubscribe from our email updates at any time.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Contact Us</h2>
        <p className="text-gray-700 mb-4">
          If you have any questions about this Privacy Policy, please contact us at{' '}
          <a href="mailto:info@shortselling.eu" className="text-blue-600 hover:text-blue-700">
            info@shortselling.eu
          </a>
        </p>
      </div>
    </div>
  );
};

export default PrivacyPage;
