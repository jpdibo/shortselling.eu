import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import CountryPage from './pages/CountryPage';
import ManagerPage from './pages/ManagerPage';
import CompanyPage from './pages/CompanyPage';
import AnalyticsPage from './pages/AnalyticsPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import DisclaimerPage from './pages/DisclaimerPage';
import './App.css';
import './styles/animations.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white">
        <Header />
        <main className="flex-grow">
                  <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/country/:countryCode" element={<CountryPage />} />
          <Route path="/manager/:managerSlug" element={<ManagerPage />} />
          <Route path="/company/:companyId" element={<CompanyPage />} />
          <Route path="/:companyName" element={<CompanyPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/disclaimer" element={<DisclaimerPage />} />
        </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
