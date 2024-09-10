import React from 'react';
import { useParams, Link } from 'react-router-dom';

const SensorPage: React.FC = () => {
    const { sensorId } = useParams<{ sensorId: string }>();

    return (
        <div>
            <h1>Sensor {sensorId}</h1>
            <Link to="/machine/1">Back to Machine</Link>
            <p>Sensor details go here</p>
        </div>
    );
};

export default SensorPage;