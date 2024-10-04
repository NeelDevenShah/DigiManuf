import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [organizationId, setOrganizationId] = useState(''); // State to store organizationId
    const { login, isLoading, error } = useAuth(); // isLoading and error from AuthContext
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await login(email, password);
            if (!error) {
                const getData = async () => {
                    try {
                        const response = await fetch(`http://localhost:3001/api/org/organization`, {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            credentials: 'include',
                        });

                        if (response.ok) {
                            const data = await response.json();
                            const id = data.data._id;
                            console.log("Fetched Organization ID:", id);
                            setOrganizationId(id); // Store the organizationId in state
                        } else {
                            console.error("Failed to fetch organization data");
                        }
                    } catch (error) {
                        console.error("Error fetching organization data:", error);
                    }
                };
                getData();
            }
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    // useEffect to navigate once organizationId is updated
    useEffect(() => {
        if (organizationId) {
            navigate(`/organization/${organizationId}`); // Navigate when organizationId is set
        }
    }, [organizationId, navigate]); // Dependency on organizationId

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6 col-lg-4">
                    <div className="card shadow">
                        <div className="card-body">
                            <h2 className="card-title text-center mb-4">Login</h2>
                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
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

                                {error && <div className="alert alert-danger">{error}</div>}

                                <button type="submit" className="btn btn-primary w-100" disabled={isLoading}>
                                    {isLoading ? 'Logging in...' : 'Login'}
                                </button>
                            </form>
                            <div className="text-center mt-3">
                                <small>Don't have an account? <a href="/signup">Sign Up</a></small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
