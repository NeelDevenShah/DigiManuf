import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const AddUser: React.FC<{ organizationId: string }> = ({ organizationId }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');

    const handleSubmit = async(e: React.FormEvent) => {
        e.preventDefault();
        // TODO: Change the URL to fetch units for the data based on the organizationId, so take the organizationId as a parameter
        const response = await fetch('http://localhost:3001/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email, password, role }),
        });

        const data = await response.json();
        console.log('Sign up response:', data);
        console.log('Add user:', email, password, role);
        setEmail('');
        setPassword('');
        setRole('');
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <div className="card shadow">
                        <div className="card-body">
                            <h2 className="card-title text-center mb-4">Add New User</h2>
                            <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                                <div className="mb-3">
                                    <div className="input-group has-validation">
                                        <span className="input-group-text">
                                            <i className="bi bi-envelope"></i>
                                        </span>
                                        <input
                                            type="email"
                                            className="form-control"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="Email"
                                            required
                                        />
                                        <div className="invalid-feedback">
                                            Please provide a valid email.
                                        </div>
                                    </div>
                                </div>
                                <div className="mb-3">
                                    <div className="input-group has-validation">
                                        <span className="input-group-text">
                                            <i className="bi bi-lock"></i>
                                        </span>
                                        <input
                                            type="password"
                                            className="form-control"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="Password"
                                            required
                                        />
                                        <div className="invalid-feedback">
                                            Please provide a password.
                                        </div>
                                    </div>
                                </div>
                                <div className="mb-3">
                                    <div className="input-group has-validation">
                                        <span className="input-group-text">
                                            <i className="bi bi-person-badge"></i>
                                        </span>
                                        <select 
                                            className="form-select" 
                                            value={role} 
                                            onChange={(e) => setRole(e.target.value)}
                                            required
                                        >
                                            <option value="">Select Role</option>
                                            <option value="admin">Admin</option>
                                            <option value="user">User</option>
                                        </select>
                                        <div className="invalid-feedback">
                                            Please select a role.
                                        </div>
                                    </div>
                                </div>
                                <button type="submit" className="btn btn-primary w-100">
                                    <i className="bi bi-person-plus me-2"></i>
                                    Add User
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AddUser;