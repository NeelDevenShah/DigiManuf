import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

interface AddMachineProps {
    unitId: string;
    organizationId?: string;
}

const AddMachine: React.FC<AddMachineProps> = ({ unitId, organizationId }) => {
    const [name, setName] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const AddMachine = async () => {
            // TODO: Change the URL to put data for the organization based on the organizationId and unitId, so takes them as a parameter
            const response = await fetch('http://localhost:3001/api/org/machine', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: name, unit:unitId }),
            });

            const data = await response.json();
            console.log('Add machine:', data);
        }
        AddMachine();
        setName('');
    };

    return (
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">Add New Machine</h5>
                <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                    <div className="mb-3">
                        <div className="input-group has-validation">
                            <span className="input-group-text" id="machine-name-addon">
                                <i className="bi bi-gear"></i>
                            </span>
                            <input
                                type="text"
                                className="form-control"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Machine Name"
                                required
                                aria-describedby="machine-name-addon machine-name-feedback"
                            />
                            <div className="invalid-feedback" id="machine-name-feedback">
                                Please provide a machine name.
                            </div>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary w-100">
                        <i className="bi bi-plus-circle me-2"></i>
                        Add Machine
                    </button>
                </form>
            </div>
            <div className="card-footer text-muted">
                <small>Adding to Unit ID: {unitId}</small>
            </div>
        </div>
    );
};

export default AddMachine;