import React, { useState } from 'react';
// Import Bootstrap CSS (assuming you've added it to your project)
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap icons for enhanced UI
import 'bootstrap-icons/font/bootstrap-icons.css';

interface AddMachineProps {
    unitId: string;
    organizationId?: string;
}

const AddMachine: React.FC<AddMachineProps> = ({ unitId, organizationId }) => {
    const [name, setName] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Implement add machine logic here
        const AddMachine = async () => {
            const response = await fetch('http://localhost:3001/api/org/machine', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ name: name, unit:unitId }),
            });

            const data = await response.json();
            console.log('Add machine:', data);
        }
        AddMachine();
        setName('');
    };

    return (
        // Added: Card component for a modern, elevated look
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">Add New Machine</h5>
                {/* Enhanced: Form with Bootstrap classes */}
                <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                    <div className="mb-3">
                        {/* Enhanced: Input group with icon for better visual cues */}
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
                    {/* Enhanced: Button with Bootstrap styling and icon */}
                    <button type="submit" className="btn btn-primary w-100">
                        <i className="bi bi-plus-circle me-2"></i>
                        Add Machine
                    </button>
                </form>
            </div>
            {/* Added: Display of current unit ID for context */}
            <div className="card-footer text-muted">
                <small>Adding to Unit ID: {unitId}</small>
            </div>
        </div>
    );
};

export default AddMachine;