import React, { useState } from 'react';
// Import Bootstrap CSS (assuming you've added it to your project)
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap icons for enhanced UI
import 'bootstrap-icons/font/bootstrap-icons.css';

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
        // Added: Container for responsive layout
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    {/* Added: Card component for a modern, elevated look */}
                    <div className="card shadow">
                        <div className="card-body">
                            <h2 className="card-title text-center mb-4">Add New User</h2>
                            {/* Enhanced: Form with Bootstrap classes */}
                            <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                                <div className="mb-3">
                                    {/* Enhanced: Input group with icon for better visual cues */}
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
                                    {/* Enhanced: Input group with icon for better visual cues */}
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
                                    {/* Enhanced: Select with custom styling */}
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
                                {/* Enhanced: Button with Bootstrap styling and icon */}
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