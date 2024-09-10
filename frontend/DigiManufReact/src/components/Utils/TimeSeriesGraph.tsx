import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

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

const TimeSeriesGraph: React.FC<{ title: string, data: { time: string, value: number }[] }> = ({ title, data }) => {
    return (
        <div style={{ marginBottom: '30px' }}>
            <h3>{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TimeSeriesGraph;
