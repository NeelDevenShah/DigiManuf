import React from 'react';
import { Link } from 'react-router-dom';
// Import Bootstrap CSS (assuming you've added it to your project)
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap icons for enhanced UI
import 'bootstrap-icons/font/bootstrap-icons.css';
import { useEffect } from 'react';

interface Sensor {
    _id: string;
    name: string;
    value?: number;
}

interface SensorListProps {
    machineId: string;
    unitId?: string;
    organizationId?: string;
    machineName: string;
}

const SensorList: React.FC<SensorListProps> = ({ machineId, unitId, organizationId, machineName}) => {
    // Fetch sensors from API or state management
    // const sensors: Sensor[] = [
    //     { _id: '1', name: 'Sensor 1' },
    //     { _id: '2', name: 'Sensor 2' },
    // ];
    const [sensors, setSensors] = React.useState<Sensor[]>([]);

    useEffect(() => {
        const getMachineList = async () => {
            const response = await fetch(`http://localhost:3001/api/org/sensor/?mid=${machineId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            const data = await response.json();
            setSensors(data.data);

            // Move the console.log here to avoid infinite re-rendering
            console.log(data.data);
        };

        getMachineList();
    }, [machineId]); // Adding machineID as a dependency ensures the useEffect runs only when it changes

    return (
        // Added: Card component for a modern, elevated look
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">
                    <i className="bi bi-cpu me-2"></i>
                    Sensors for Machine {machineName}
                </h5>
                {/* Enhanced: List group for better structure and styling */}
                <div className="list-group">
                    {sensors.map((sensor) => (
                        <Link
                            key={sensor._id}
                            to={`/sensor/${sensor._id}`}
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