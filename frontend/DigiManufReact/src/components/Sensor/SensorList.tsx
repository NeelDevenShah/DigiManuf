import React from 'react';
import { Link } from 'react-router-dom';

interface Sensor {
    id: string;
    name: string;
}

interface SensorListProps {
    machineId: string;
}

const SensorList: React.FC<SensorListProps> = ({ machineId }) => {
    // Fetch sensors from API or state management
    const sensors: Sensor[] = [
        { id: '1', name: 'Sensor 1' },
        { id: '2', name: 'Sensor 2' },
    ];

    return (
        <div>
            {sensors.map((sensor) => (
                <div key={sensor.id}>
                    <Link to={`/sensor/${sensor.id}`}>{sensor.name}</Link>
                </div>
            ))}
        </div>
    );
};

export default SensorList;