import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';
import OrganizationPage from './pages/OrganizationPage';
import UnitPage from './pages/UnitPage';
import MachinePage from './pages/MachinePage';
import SensorPage from './pages/SensorPage';

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* The code does not have the organization Id which is required for the entire setup, And here in argument we have to pass all the ids hierarchically to all the components */}
                    {/* path="/machine/:machineId/unit/:unitId/organization/:organizationId", which means the machine page with parameters machineId, unitId, organizationId */}
                    <Route path="/" element={<LoginPage />} />
                    <Route path="/signup" element={<SignUpPage />} />
                    <Route path="/organization" element={<OrganizationPage />} />
                    <Route path="/unit/:unitId" element={<UnitPage />} />
                    <Route path="/machine/:machineId" element={<MachinePage />} />
                    <Route path="/sensor/:sensorId" element={<SensorPage />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;