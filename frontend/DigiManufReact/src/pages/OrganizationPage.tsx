import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
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

// Define similar dummyData3, dummyData4, dummyData5...

const OrganizationPage: React.FC = () => {
    return (
        <div>
            <h1>Organization Dashboard</h1>
            <OrganizationDashboard />
            <h2>Users</h2>
            <AddUser />
            <h2>Manufacturing Units</h2>
            <UnitList />
            <AddUnit />

            <h2>Time Series Graphs</h2>
            <TimeSeriesGraph title="Graph 1: Unit Performance" data={dummyData1} />
            <TimeSeriesGraph title="Graph 2: Energy Consumption" data={dummyData2} />
            {/* Similarly, pass dummyData3, dummyData4, dummyData5 */}
        </div>
    );
};

export default OrganizationPage;
