import React from 'react';
import { useParams, Link } from 'react-router-dom';
import SensorList from '../components/Sensor/SensorList';
import AddSensor from '../components/Sensor/AddSensor';
import TimeSeriesGraph from '../components/Utils/TimeSeriesGraph';
import { useEffect } from 'react';

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
        justifyContent: 'space-between',
        gap: '20px',
    },
    graphCard: {
        flex: '1',
        backgroundColor: '#fff',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    },
};

const MachinePage: React.FC = () => {
    const {organizationId, unitId, machineId} = useParams<{ organizationId: string, unitId: string, machineId: string }>();
    const [name, setName] = React.useState<string>('');

    useEffect(() => {
        const getName = async () => {
            // TODO: Change the URL to fetch data for the organization based on the organizationId and unitid, so take them as a parameter
            const response = await fetch(`http://localhost:3001/api/org/machine/?mid=${machineId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            const data = await response.json();
            setName(data.data[0].name);
        };

        getName();
    }, [machineId]);


    if (!machineId) return <div>Machine not found</div>;

    return (
        <div style={styles.container}>
            <h1 style={styles.pageTitle}>{name}</h1>
            <Link to={`/unit/${organizationId}/${unitId}`} style={styles.link}>Back to Unit</Link>

            {/* Sensors Section */}
            <div style={styles.card}>
                <h2 style={styles.sectionTitle}>Sensors</h2>
                <SensorList machineId={machineId} unitId = {unitId} organizationId= {organizationId} machineName={name}/>
                <hr/>
                <AddSensor machineId={machineId} unitId = {unitId} organizationId= {organizationId}  />
            </div>

            {/* Graph Section */}
            <div style={styles.card}>
                <h2 style={styles.sectionTitle}>Time Series Graphs</h2>
                <div style={styles.graphContainer}>
                    <div style={styles.graphCard}>
                        <TimeSeriesGraph title="Graph 1: Unit Performance" data={dummyData1} unitId = {unitId} organizationId= {organizationId}/>
                    </div>
                    <div style={styles.graphCard}>
                        <TimeSeriesGraph title="Graph 2: Energy Consumption" data={dummyData2} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MachinePage;
