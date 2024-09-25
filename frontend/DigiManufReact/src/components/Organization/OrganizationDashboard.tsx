import React from 'react';
// Import Bootstrap CSS (assuming you've added it to your project)
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap icons for enhanced UI
import 'bootstrap-icons/font/bootstrap-icons.css';
import { useState } from 'react';

const getData = async () => {
    // Fetch data from the API
    const [unit, setUnit] = useState([]);
    const [machine, setMachine] = useState([]);
    const [sensor, setSensor] = useState([]);
    const response = await fetch('http://localhost:3001/api/organization');
    const data = await response.json();
    console.log('Organization data:', data);
}

const OrganizationDashboard: React.FC = () => {
    return (
        // Added: Container for responsive layout
        <div className="container mt-4">
            {/* Added: Row for grid layout */}
            <div className="row">
                <div className="col-12">
                    {/* Enhanced: Card component for a modern, elevated look */}
                    <div className="card shadow-sm">
                        <div className="card-body">
                            {/* Enhanced: Heading with icon and styling */}
                            <h2 className="card-title mb-4">
                                <i className="bi bi-building me-2"></i>
                                Organization Overview
                            </h2>
                            {/* Added: Row for responsive grid layout of stats */}
                            <div className="row">
                                {/* Enhanced: Each stat in its own card */}
                                <div className="col-md-4 mb-3">
                                    <div className="card bg-light">
                                        <div className="card-body text-center">
                                            <h5 className="card-title">
                                                <i className="bi bi-boxes me-2"></i>
                                                Total Units
                                            </h5>
                                            <p className="card-text display-4">5</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-4 mb-3">
                                    <div className="card bg-light">
                                        <div className="card-body text-center">
                                            <h5 className="card-title">
                                                <i className="bi bi-gear me-2"></i>
                                                Total Machines
                                            </h5>
                                            <p className="card-text display-4">25</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-4 mb-3">
                                    <div className="card bg-light">
                                        <div className="card-body text-center">
                                            <h5 className="card-title">
                                                <i className="bi bi-cpu me-2"></i>
                                                Total Sensors
                                            </h5>
                                            <p className="card-text display-4">100</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OrganizationDashboard;