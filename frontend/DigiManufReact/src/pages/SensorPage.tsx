import React, { useEffect } from 'react';
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

const styles: { [key: string]: React.CSSProperties } = {
    container: {
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '20px',
    },
    card: {
        backgroundColor: '#fff',
        padding: '20px',
        marginBottom: '20px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    },
    pageTitle: {
        textAlign: 'center',
        fontSize: '36px',
        color: '#333',
        marginBottom: '20px',
        fontWeight: 'bold',
    },
    link: {
        display: 'block',
        textAlign: 'center',
        fontSize: '18px',
        color: '#0066cc',
        textDecoration: 'none',
        marginBottom: '30px',
    },
    sectionTitle: {
        fontSize: '24px',
        color: '#222',
        marginBottom: '15px',
        textAlign: 'center',
        fontWeight: 'bold',
    },
    graphContainer: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
    },
};

const SensorPage: React.FC = () => {
    const {organizationId, unitId, machineId, sensorId } = useParams<{organizationId: string, unitId: string, machineId: string,  sensorId: string}>();
    const [sensor, setSensor] = React.useState<any>();

    useEffect(() => {
        let getName = async()=>{
            // TODO: Change the URL to fetch data for the organization based on the organizationId, so take the organizationId, unitId, machineId as a parameter
            const response = await fetch(`http://localhost:3001/api/org/sensor/?sid=${sensorId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });
            const data = await response.json();
            setSensor(data.data.name);
            console.log(sensor)
        }
        getName();
    },[sensorId])

    if (!sensorId) return <div>Sensor not found</div>;

    return (
        <div style={styles.container}>
            <h1 style={styles.pageTitle}>Sensor {sensor}</h1>
            <Link to={`/machine/${organizationId}/${unitId}/${machineId}`} style={styles.link}>Back to Machine</Link>
            <p style={styles.card}>Sensor details go here</p>


            <div style={styles.card}>
                <h2 style={styles.sectionTitle}>Time Series Graphs</h2>
                <div style={styles.graphContainer}>
                    <TimeSeriesGraph title="Graph 1: Unit Performance" data={dummyData1} />
                    <TimeSeriesGraph title="Graph 2: Energy Consumption" data={dummyData2} />
                    <TimeSeriesGraph title="Graph 3: Unit Performance" data={dummyData3} />
                    <TimeSeriesGraph title="Graph 4: Energy Consumption" data={dummyData4} />
                    <TimeSeriesGraph title="Graph 5: Unit Performance" data={dummyData5} />
                </div>
            </div>
        </div>
    );
};

export default SensorPage;
