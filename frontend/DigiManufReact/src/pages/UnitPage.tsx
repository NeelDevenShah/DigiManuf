import React from 'react';
import { useParams, Link } from 'react-router-dom';
import MachineList from '../components/Machine/MachineList';
import AddMachine from '../components/Machine/AddMachine';

const UnitPage: React.FC = () => {
    const { unitId } = useParams<{ unitId: string }>();

    if (!unitId) return <div>Unit not found</div>;

    return (
        <div>
            <h1>Unit {unitId}</h1>
            <Link to="/organization">Back to Organization</Link>
            <h2>Machines</h2>
            <MachineList unitId={unitId} />
            <AddMachine unitId={unitId} />
        </div>
    );
};

export default UnitPage;