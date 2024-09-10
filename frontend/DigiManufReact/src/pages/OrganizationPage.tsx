import React from 'react';
import OrganizationDashboard from '../components/Organization/OrganizationDashboard';
import AddUser from '../components/Organization/AddUser';
import UnitList from '../components/Unit/UnitList';
import AddUnit from '../components/Unit/AddUnit';

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
        </div>
    );
};

export default OrganizationPage;