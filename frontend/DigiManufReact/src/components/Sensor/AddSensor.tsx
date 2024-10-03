import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

interface AddSensorProps {
    machineId: string;
    unitId?: string;
    organizationId?: string;
}

const AddSensor: React.FC<AddSensorProps> = ({ machineId, unitId, organizationId}) => {
    const [name, setName] = useState('');
    const [type, setType] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const addSensor = async () => {
            // TODO: Change the URL to put units for the data based on the organizationId and unitId, so takes them as a parameter
            const response = await fetch('http://localhost:3001/api/org/sensor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },  
                body: JSON.stringify({ name: name, machine:machineId, type:type }),
            });

            const data = await response.json();
            console.log('Add sensor:', data);
        }
        addSensor();
        setName('');
    };

    return (
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">
                    <i className="bi bi-plus-circle me-2"></i>
                    Add New Sensor
                </h5>
                <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                    <div className="mb-3">
                        <div className="input-group has-validation">
                            <span className="input-group-text">
                                <i className="bi bi-tag"></i>
                            </span>
                            <input
                                type="text"
                                className="form-control"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Sensor Name"
                                required
                            />
                            <div className="invalid-feedback">
                                Please provide a sensor name.
                            </div>
                        </div>
                    </div>
                    <div className="mb-3">
                        <div className="input-group has-validation">
                            <span className="input-group-text">
                                <i className="bi bi-cpu"></i>
                            </span>
                            <input
                                type="text"
                                className="form-control"
                                value={type}
                                onChange={(e) => setType(e.target.value)}
                                placeholder="Sensor Type"
                                required
                            />
                            <div className="invalid-feedback">
                                Please provide a sensor type.
                            </div>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary w-100">
                        <i className="bi bi-plus-circle me-2"></i>
                        Add Sensor
                    </button>
                </form>
            </div>
            <div className="card-footer text-muted">
                <small>Adding to Machine ID: {machineId}</small>
            </div>
        </div>
    );
};

export default AddSensor;