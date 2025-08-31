import React from 'react';

const TermsPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Terms of Use</h1>
      
      <div className="prose prose-lg max-w-none">
        <p className="text-gray-600 mb-4">
          <strong>Last updated:</strong> {new Date().toLocaleDateString()}
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Acceptance of Terms</h2>
        <p className="text-gray-700 mb-4">
          By accessing and using ShortSelling.eu, you accept and agree to be bound by the terms and provision of this agreement.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Use License</h2>
        <p className="text-gray-700 mb-4">
          Permission is granted to temporarily download one copy of the materials (information or software) on ShortSelling.eu for personal, non-commercial transitory viewing only.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. Data Accuracy</h2>
        <p className="text-gray-700 mb-4">
          The information on this website is provided "as is" without any representations or warranties, express or implied. ShortSelling.eu makes no representations or warranties in relation to this website or the information and materials provided on this website.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Data Sources</h2>
        <p className="text-gray-700 mb-4">
          All data presented on this website is sourced from publicly available regulatory websites across Europe. ShortSelling.eu is not affiliated with any regulatory authorities and does not guarantee the accuracy, completeness, or timeliness of the information.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Limitation of Liability</h2>
        <p className="text-gray-700 mb-4">
          ShortSelling.eu will not be liable to you (whether under the law of contact, the law of torts or otherwise) in relation to the contents of, or use of, or otherwise in connection with, this website for any indirect, special or consequential loss.
        </p>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Contact Information</h2>
        <p className="text-gray-700 mb-4">
          For questions about these Terms of Use, please contact us at{' '}
          <a href="mailto:info@shortselling.eu" className="text-blue-600 hover:text-blue-700">
            info@shortselling.eu
          </a>
        </p>
      </div>
    </div>
  );
};

export default TermsPage;
