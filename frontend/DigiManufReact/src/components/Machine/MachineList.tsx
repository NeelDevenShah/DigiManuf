import React from 'react';
import { Link } from 'react-router-dom';

interface Machine {
    id: string;
    name: string;
}

interface MachineListProps {
    unitId: string;
}

const MachineList: React.FC<MachineListProps> = ({ unitId }) => {
    // Fetch machines from API or state management
    const machines: Machine[] = [
        { id: '1', name: 'Machine 1' },
        { id: '2', name: 'Machine 2' },
    ];

    return (
        <div>
            {machines.map((machine) => (
                <div key={machine.id}>
                    <Link to={`/machine/${machine.id}`}>{machine.name}</Link>
                </div>
            ))}
        </div>
    );
};

export default MachineList;