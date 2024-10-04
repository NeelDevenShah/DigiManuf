import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const SignUp: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [organization, setOrganization] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // Implement sign up logic here
        const response = await fetch('http://localhost:3001/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email, password, organization }),
        });

        const data = await response.json();
        console.log('Sign up response:', data);

        // navigate('/');
    };

    return (
        // Added: Container for responsive layout and centering
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6 col-lg-4">
                    {/* Added: Card component for a modern, elevated look */}
                    <div className="card shadow">
                        <div className="card-body">
                            {/* Added: Title for the form */}
                            <h2 className="card-title text-center mb-4">Sign Up</h2>
                            {/* Enhanced: Form with Bootstrap classes */}
                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    {/* Enhanced: Input group with icon for better visual cues */}
                                    <div className="input-group">
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
                                    </div>
                                </div>
                                <div className="mb-3">
                                    {/* Enhanced: Input group with icon for better visual cues */}
                                    <div className="input-group">
                                        <span className="input-group-text">
                                            <i className="bi bi-envelope"></i>
                                        </span>
                                        <input
                                            type="organization"
                                            className="form-control"
                                            value={organization}
                                            onChange={(e) => setOrganization(e.target.value)}
                                            placeholder="Organization"
                                            required
                                        />
                                    </div>
                                </div>
                                <div className="mb-3">
                                    {/* Enhanced: Input group with icon for better visual cues */}
                                    <div className="input-group">
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
                                    </div>
                                </div>
                                {/* Enhanced: Button with Bootstrap styling */}
                                <button type="submit" className="btn btn-primary w-100">
                                    Sign Up
                                </button>
                            </form>
                            {/* Added: Link to login page for better user flow */}
                            <div className="text-center mt-3">
                                <small>Already have an account? <a href="/">Log in</a></small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SignUp;