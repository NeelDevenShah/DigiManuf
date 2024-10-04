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
    const [sensors, setSensors] = React.useState<Sensor[]>([]);

    useEffect(() => {
        const getMachineList = async () => {
            // TODO: Change the URL to fetch data for the organization based on the organizationId and unitId, so take the organizationId as a parameter
            const response = await fetch(`http://localhost:3001/api/org/sensor/?mid=${machineId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            const data = await response.json();
            setSensors(data.data);

            console.log(data.data);
        };

        getMachineList();
    }, [machineId]); // Adding machineID as a dependency ensures the useEffect runs only when it changes

    return (
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">
                    <i className="bi bi-cpu me-2"></i>
                    Sensors for Machine {machineName}
                </h5>
                <div className="list-group">
                    {sensors.map((sensor) => (
                        <Link
                            key={sensor._id}
                            to={`/sensor/${organizationId}/${unitId}/${machineId}/${sensor._id}`}
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
                <hr/>
            </div>
            <div className="card-footer text-muted">
                <small>Total Sensors: {sensors.length}</small>
            </div>
        </div>
    );
};

export default SensorList;