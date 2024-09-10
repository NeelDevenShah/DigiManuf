import React from 'react';
import { Link } from 'react-router-dom';

interface Unit {
    id: string;
    name: string;
}

const UnitList: React.FC = () => {
    // Fetch units from API or state management
    const units: Unit[] = [
        { id: '1', name: 'Unit 1' },
        { id: '2', name: 'Unit 2' },
    ];

    return (
        <div>
            {units.map((unit) => (
                <div key={unit.id}>
                    <Link to={`/unit/${unit.id}`}>{unit.name}</Link>
                </div>
            ))}
        </div>
    );
};

export default UnitList;