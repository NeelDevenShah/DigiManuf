import React from 'react';
import { Link } from 'react-router-dom';
// Import Bootstrap CSS (assuming you've added it to your project)
import 'bootstrap/dist/css/bootstrap.min.css';
// Import Bootstrap icons for enhanced UI
import 'bootstrap-icons/font/bootstrap-icons.css';

interface Machine {
    id: string;
    name: string;
}

interface MachineListProps {
    unitId: string;
}

const MachineList: React.FC<MachineListProps> = ({ unitId }) => {
    // Fetch machines from API or state management
    const machines: Machine[] = [
        { id: '1', name: 'Machine 1' },
        { id: '2', name: 'Machine 2' },
    ];

    return (
        // Added: Card component for a modern, elevated look
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">
                    <i className="bi bi-gear-fill me-2"></i>
                    Machines in Unit {unitId}
                </h5>
                {/* Enhanced: List group for better structure and styling */}
                <div className="list-group">
                    {machines.map((machine) => (
                        <Link
                            key={machine.id}
                            to={`/machine/${machine.id}`}
                            className="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                        >
                            <span>
                                <i className="bi bi-tools me-2"></i>
                                {machine.name}
                            </span>
                            <i className="bi bi-chevron-right text-muted"></i>
                        </Link>
                    ))}
                </div>
                {/* Added: Button to add new machine */}
                <Link to={`/unit/${unitId}/add-machine`} className="btn btn-primary mt-3 w-100">
                    <i className="bi bi-plus-circle me-2"></i>
                    Add New Machine
                </Link>
            </div>
            {/* Added: Card footer with machine count */}
            <div className="card-footer text-muted">
                <small>Total Machines: {machines.length}</small>
            </div>
        </div>
    );
};

export default MachineList;