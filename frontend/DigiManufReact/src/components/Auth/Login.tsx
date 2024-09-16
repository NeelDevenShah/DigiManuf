import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await login(email, password);
            navigate('/organization');
        } catch (error) {
            console.error('Login failed:', error);
            // Added: Show error message to user
            alert('Login failed. Please try again.');
        }
    };

    return (
        // Added: Container for centering and responsive layout
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6 col-lg-4">
                    {/* Added: Card component for a modern look */}
                    <div className="card shadow">
                        <div className="card-body">
                            <h2 className="card-title text-center mb-4">Login</h2>
                            {/* Enhanced: Form with Bootstrap classes */}
                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    {/* Enhanced: Input group with icon */}
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
                                    {/* Enhanced: Input group with icon */}
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
                                    Login
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;