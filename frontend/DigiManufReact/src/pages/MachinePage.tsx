import React from 'react';
import { useParams, Link } from 'react-router-dom';
import SensorList from '../components/Sensor/SensorList';
import AddSensor from '../components/Sensor/AddSensor';
import TimeSeriesGraph from '../components/Utils/TimeSeriesGraph';

const dummyData1 = [
    { time: '10:00', value: 400 },
    { time: '10:30', value: 300 },
    { time: '11:00', value: 500 },
    { time: '11:30', value: 200 },
    { time: '12:00', value: 600 },
  ];
  
  const dummyData2 = [
    { time: '10:00', value: 100 },
    { time: '10:30', value: 200 },
    { time: '11:00', value: 150 },
    { time: '11:30', value: 250 },
    { time: '12:00', value: 350 },
  ];
  
  // Define similar dummyData3, dummyData4, dummyData5...

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
            <h2>Time Series Graphs</h2>
            <TimeSeriesGraph title="Graph 1: Unit Performance" data={dummyData1} />
            <TimeSeriesGraph title="Graph 2: Energy Consumption" data={dummyData2} />
            {/* Similarly, pass dummyData3, dummyData4, dummyData5 */}
        </div>
    );
};

export default MachinePage;