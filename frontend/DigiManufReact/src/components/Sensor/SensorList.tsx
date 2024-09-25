import React from 'react';
import { Link } from 'react-router-dom';
// Import Bootstrap CSS (assuming you've added it to your project)
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap icons for enhanced UI
import 'bootstrap-icons/font/bootstrap-icons.css';

interface Sensor {
    id: string;
    name: string;
}

interface SensorListProps {
    machineId: string;
    unitId?: string;
    organizationId?: string;
}

const SensorList: React.FC<SensorListProps> = ({ machineId, unitId, organizationId}) => {
    // Fetch sensors from API or state management
    const sensors: Sensor[] = [
        { id: '1', name: 'Sensor 1' },
        { id: '2', name: 'Sensor 2' },
    ];

    return (
        // Added: Card component for a modern, elevated look
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">
                    <i className="bi bi-cpu me-2"></i>
                    Sensors for Machine {machineId}
                </h5>
                {/* Enhanced: List group for better structure and styling */}
                <div className="list-group">
                    {sensors.map((sensor) => (
                        <Link
                            key={sensor.id}
                            to={`/sensor/${sensor.id}`}
                            className="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                        >
                            <span>
                                <i className="bi bi-thermometer me-2"></i>
                                {sensor.name}
                            </span>
                            <i className="bi bi-chevron-right text-muted"></i>
                        </Link>
                    ))}
                </div>
                {/* Added: Button to add new sensor */}
                <Link to={`/machine/${machineId}/add-sensor`} className="btn btn-primary mt-3 w-100">
                    <i className="bi bi-plus-circle me-2"></i>
                    Add New Sensor
                </Link>
            </div>
            {/* Added: Card footer with sensor count */}
            <div className="card-footer text-muted">
                <small>Total Sensors: {sensors.length}</small>
            </div>
        </div>
    );
};

export default SensorList;