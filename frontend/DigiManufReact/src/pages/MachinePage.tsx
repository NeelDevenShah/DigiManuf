import React from 'react';
import { useParams, Link } from 'react-router-dom';
import SensorList from '../components/Sensor/SensorList';
import AddSensor from '../components/Sensor/AddSensor';

const MachinePage: React.FC = () => {
    const { machineId } = useParams<{ machineId: string }>();

    if (!machineId) return <div>Machine not found</div>;

    return (
        <div>
            <h1>Machine {machineId}</h1>
            <Link to="/unit/1">Back to Unit</Link>
            <h2>Sensors</h2>
            <SensorList machineId={machineId} />
            <AddSensor machineId={machineId} />
        </div>
    );
};

export default MachinePage;