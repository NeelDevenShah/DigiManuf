import React from 'react';
import { useParams, Link } from 'react-router-dom';
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
  
  const dummyData3 = [
    { time: '10:00', value: 400 },
    { time: '10:30', value: 300 },
    { time: '11:00', value: 500 },
    { time: '11:30', value: 200 },
    { time: '12:00', value: 600 },
  ];
  
  const dummyData4 = [
    { time: '10:00', value: 100 },
    { time: '10:30', value: 200 },
    { time: '11:00', value: 150 },
    { time: '11:30', value: 250 },
    { time: '12:00', value: 350 },
  ];

  const dummyData5 = [
    { time: '10:00', value: 400 },
    { time: '10:30', value: 300 },
    { time: '11:00', value: 500 },
    { time: '11:30', value: 200 },
    { time: '12:00', value: 600 },
  ];

const SensorPage: React.FC = () => {
    const { sensorId } = useParams<{ sensorId: string }>();

    return (
        <div>
            <h1>Sensor {sensorId}</h1>
            <Link to="/machine/1">Back to Machine</Link>
            <p>Sensor details go here</p>

            <h2>Time Series Graphs</h2>
            <TimeSeriesGraph title="Graph 1: Unit Performance" data={dummyData1} />
            <TimeSeriesGraph title="Graph 2: Energy Consumption" data={dummyData2} />
            <TimeSeriesGraph title="Graph 3: Unit Performance" data={dummyData3} />
            <TimeSeriesGraph title="Graph 4: Energy Consumption" data={dummyData4} />
            <TimeSeriesGraph title="Graph 5: Unit Performance" data={dummyData5} />
        </div>
    );
};

export default SensorPage;