import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';
import OrganizationPage from './pages/OrganizationPage';
import UnitPage from './pages/UnitPage';
import MachinePage from './pages/MachinePage';
import SensorPage from './pages/SensorPage';

// TODO: Reloading of the page or component when any of the new things is added to it.

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<LoginPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/signup" element={<SignUpPage />} />
                    <Route path="/organization/:organizationId" element={<OrganizationPage />} />
                    <Route path="/unit/:organizationId/:unitId/" element={<UnitPage />} />
                    <Route path="/machine/:organizationId/:unitId/:machineId" element={<MachinePage />} />
                    <Route path="/sensor/:organizationId/:unitId/:machineId/:sensorId" element={<SensorPage />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;