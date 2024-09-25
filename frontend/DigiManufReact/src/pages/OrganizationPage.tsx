import React from 'react';
import { Link } from 'react-router-dom';
import OrganizationDashboard from '../components/Organization/OrganizationDashboard';
import AddUser from '../components/Organization/AddUser';
import UnitList from '../components/Unit/UnitList';
import AddUnit from '../components/Unit/AddUnit';
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

const OrganizationPage: React.FC = () => {
    return (
        <div style={styles.container}>
            <h1 style={styles.pageTitle}>Organization Dashboard</h1>
            <Link to="/" style={styles.link}>Back to Home</Link>

            {/* Dashboard Section */}
            <div style={styles.card}>
                <h2 style={styles.sectionTitle}>Overview</h2>
                <OrganizationDashboard />
            </div>

            {/* Users Section */}
            <div style={styles.card}>
                <h2 style={styles.sectionTitle}>Users</h2>
                <AddUser />
            </div>

            {/* Manufacturing Units Section */}
            <div style={styles.card}>
                <h2 style={styles.sectionTitle}>Manufacturing Units</h2>
                <UnitList />
                <AddUnit />
            </div>

            {/* Graph Section */}
            <div style={styles.card}>
                <h2 style={styles.sectionTitle}>Time Series Graphs</h2>
                <div style={styles.graphContainer}>
                    <div style={styles.graphCard}>
                        <TimeSeriesGraph title="Graph 1: Unit Performance" data={dummyData1} />
                    </div>
                    <div style={styles.graphCard}>
                        <TimeSeriesGraph title="Graph 2: Energy Consumption" data={dummyData2} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OrganizationPage;