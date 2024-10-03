import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const AddUnit: React.FC<{ organizationId: string }> = ({ organizationId }) =>  {
    const [name, setName] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // TODO: Change the URL to put units for the data based on the organizationId, so take the organizationId as a parameter
        const response = await fetch('http://localhost:3001/api/org/unit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name }),
        });

        const data = await response.json();

        console.log('Add unit:', data);
        setName('');
    };

    return (
        <div className="container mt-4">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <div className="card shadow">
                        <div className="card-body">
                            <h2 className="card-title text-center mb-4">Add New Unit</h2>
                            <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                                <div className="mb-3">
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