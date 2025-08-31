import React from 'react';

const DisclaimerPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Disclaimer</h1>
      
      <div className="prose prose-lg max-w-none">
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>Important Notice:</strong> Please read this disclaimer carefully before using our service.
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Official Disclaimer</h2>
          <p className="text-gray-700 mb-4">
            <strong>ShortSelling.eu is not affiliated with any European financial regulatory authorities.</strong> 
            The information on this website is based on publicly available short-selling registers which are 
            published by European regulatory authorities and their sister organizations.
          </p>
          
          <p className="text-gray-700 mb-4">
            More information about the registers and links to the official registers themselves are available 
            on the respective pages of the regulatory authority websites. ShortSelling.eu makes no guarantees 
            about the accuracy of the information on this website.
          </p>
          
          <p className="text-gray-700 mb-4">
            For questions and comments, please contact us via{' '}
            <a href="mailto:info@shortselling.eu" className="text-blue-600 hover:text-blue-700 font-medium">
              info@shortselling.eu
            </a>
          </p>
        </div>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Data Sources and Accuracy</h2>
        <p className="text-gray-700 mb-4">
          All data presented on ShortSelling.eu is sourced from official regulatory websites across Europe. 
          These include but are not limited to:
        </p>
        
        <ul className="list-disc list-inside text-gray-700 mb-6 space-y-2">
          <li>Danish Financial Supervisory Authority (Finanstilsynet)</li>
          <li>Norwegian Financial Supervisory Authority (Finanstilsynet)</li>
          <li>Swedish Financial Supervisory Authority (Finansinspektionen)</li>
          <li>Finnish Financial Supervisory Authority (Finanssivalvonta)</li>
          <li>Spanish National Securities Market Commission (CNMV)</li>
          <li>German Federal Financial Supervisory Authority (BaFin)</li>
          <li>French Financial Markets Authority (AMF)</li>
          <li>Italian Companies and Exchange Commission (CONSOB)</li>
          <li>UK Financial Conduct Authority (FCA)</li>
          <li>Dutch Authority for the Financial Markets (AFM)</li>
          <li>Belgian Financial Services and Markets Authority (FSMA)</li>
          <li>Central Bank of Ireland</li>
          <li>Polish Financial Supervision Authority (KNF)</li>
          <li>Austrian Financial Market Authority (FMA)</li>
        </ul>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Limitations of Use</h2>
        <p className="text-gray-700 mb-4">
          The information provided on this website is for informational purposes only and should not be 
          considered as financial advice. Users should:
        </p>
        
        <ul className="list-disc list-inside text-gray-700 mb-6 space-y-2">
          <li>Always verify information with official sources before making any investment decisions</li>
          <li>Understand that data may be delayed or incomplete</li>
          <li>Not rely solely on this information for trading or investment purposes</li>
          <li>Consult with qualified financial advisors for investment advice</li>
        </ul>
        
        <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Technical Disclaimers</h2>
        <p className="text-gray-700 mb-4">
          While we strive to maintain accurate and up-to-date information, we cannot guarantee:
        </p>
        
        <ul className="list-disc list-inside text-gray-700 mb-6 space-y-2">
          <li>The accuracy, completeness, or timeliness of the data</li>
          <li>Continuous availability of the service</li>
          <li>Freedom from technical errors or interruptions</li>
          <li>Compatibility with all devices or browsers</li>
        </ul>
        
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mt-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <strong>Contact:</strong> For questions about this disclaimer or our data sources, 
                please contact us at{' '}
                <a href="mailto:info@shortselling.eu" className="text-blue-600 hover:text-blue-700 font-medium">
                  info@shortselling.eu
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DisclaimerPage;
