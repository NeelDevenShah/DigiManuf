import React, { useState } from 'react';

const AddUnit: React.FC = () => {
    const [name, setName] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Implement add unit logic here
        console.log('Add unit:', name);
        setName('');
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Unit Name"
                required
            />
            <button type="submit">Add Unit</button>
        </form>
    );
};

export default AddUnit;