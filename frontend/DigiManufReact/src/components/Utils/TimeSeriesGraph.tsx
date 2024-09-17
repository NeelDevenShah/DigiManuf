import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

// Dummy data definitions remain unchanged
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

interface TimeSeriesGraphProps {
  title: string;
  data: { time: string; value: number }[];
}

const TimeSeriesGraph: React.FC<TimeSeriesGraphProps> = ({ title, data }) => {
  return (
    // Added Bootstrap card component for a more professional look
    <div className="card shadow-sm mb-4">
      {/* Used card-header for the title with Bootstrap styling */}
      <div className="card-header bg-primary text-white d-flex align-items-center">
        {/* Added an icon for visual enhancement */}
        <i className="bi bi-graph-up me-2"></i>
        <h3 className="mb-0">{title}</h3>
      </div>
      {/* Wrapped the chart in card-body for proper padding */}
      <div className="card-body">
        {/* Made the container fluid for better responsiveness */}
        <div className="container-fluid p-0">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              {/* Changed the line color to match Bootstrap's primary color */}
              <Line type="monotone" dataKey="value" stroke="#0d6efd" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Example usage of the component
const App: React.FC = () => {
  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-md-6">
          <TimeSeriesGraph title="Graph 1" data={dummyData1} />
        </div>
        <div className="col-md-6">
          <TimeSeriesGraph title="Graph 2" data={dummyData2} />
        </div>
      </div>
    </div>
  );
};

export default TimeSeriesGraph;
