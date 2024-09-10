import React, { useState } from 'react';

interface AddMachineProps {
    unitId: string;
}

const AddMachine: React.FC<AddMachineProps> = ({ unitId }) => {
    const [name, setName] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Implement add machine logic here
        console.log('Add machine:', name, 'to unit:', unitId);
        setName('');
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Machine Name"
                required
            />
            <button type="submit">Add Machine</button>
        </form>
    );
};

export default AddMachine;