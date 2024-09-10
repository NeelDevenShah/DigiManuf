import React, { useState } from 'react';

interface AddSensorProps {
    machineId: string;
}

const AddSensor: React.FC<AddSensorProps> = ({ machineId }) => {
    const [name, setName] = useState('');
    const [type, setType] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Implement add sensor logic here
        console.log('Add sensor:', name, type, 'to machine:', machineId);
        setName('');
        setType('');
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Sensor Name"
                required
            />
            <input
                type="text"
                value={type}
                onChange={(e) => setType(e.target.value)}
                placeholder="Sensor Type"
                required
            />
            <button type="submit">Add Sensor</button>
        </form>
    );
};

export default AddSensor;