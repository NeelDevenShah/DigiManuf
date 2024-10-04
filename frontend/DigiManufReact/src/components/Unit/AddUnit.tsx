import React, { useState } from 'react';
// Import Bootstrap CSS (assuming you've added it to your project)
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap icons for enhanced UI
import 'bootstrap-icons/font/bootstrap-icons.css';

const AddUnit: React.FC = () => {
    const [name, setName] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // Implement add unit logic here
        const response = await fetch('http://localhost:3001/api/org/unit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ name: name }),
        });

        const data = await response.json();

        console.log('Add unit:', data);
        setName('');
    };

    return (
        // Added: Container for responsive layout
        <div className="container mt-4">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    {/* Added: Card component for a modern, elevated look */}
                    <div className="card shadow">
                        <div className="card-body">
                            <h2 className="card-title text-center mb-4">Add New Unit</h2>
                            {/* Enhanced: Form with Bootstrap classes */}
                            <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                                <div className="mb-3">
                                    {/* Enhanced: Input group with icon for better visual cues */}
                                    <div className="input-group has-validation">
                                        <span className="input-group-text">
                                            <i className="bi bi-building"></i>
                                        </span>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={name}
                                            name="name"
                                            onChange={(e) => setName(e.target.value)}
                                            placeholder="Unit Name"
                                            required
                                        />
                                        <div className="invalid-feedback">
                                            Please provide a unit name.
                                        </div>
                                    </div>
                                </div>
                                {/* Enhanced: Button with Bootstrap styling and icon */}
                                <button type="submit" className="btn btn-primary w-100">
                                    <i className="bi bi-plus-circle me-2"></i>
                                    Add Unit
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AddUnit;