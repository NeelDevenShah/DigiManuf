import React, { useState } from 'react';

const AddUser: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Implement add user logic here
        console.log('Add user:', email, password, role);
        setEmail('');
        setPassword('');
        setRole('');
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                required
            />
            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
            />
            <select value={role} onChange={(e) => setRole(e.target.value)} required>
                <option value="">Select Role</option>
                <option value="admin">Admin</option>
                <option value="user">User</option>
            </select>
            <button type="submit">Add User</button>
        </form>
    );
};

export default AddUser;