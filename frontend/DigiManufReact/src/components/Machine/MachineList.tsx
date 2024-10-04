import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

interface Machine {
    _id: string;
    name: string;
    sensors: string[];
    unit: string;
}

interface MachineListProps {
    unitId: string;
    organizationId?: string;
    unitName: string;
}

const MachineList: React.FC<MachineListProps> = ({ unitId, organizationId, unitName }) => {
    const [machines, setMachines] = React.useState<Machine[]>([]);

    useEffect(() => {
        const getMachineList = async () => {
            // TODO: Change the URL to fetch data for the organization based on the organizationId, so take the organizationId as a parameter
            const response = await fetch(`http://localhost:3001/api/org/machine/?id=${unitId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            const data = await response.json();
            setMachines(data.data);

            console.log(data.data);
        };

        getMachineList();
    }, [unitId]); // Adding unitId as a dependency ensures the useEffect runs only when it changes

    return (
        <div className="card shadow-sm">
            <div className="card-body">
                <h5 className="card-title mb-3">
                    <i className="bi bi-gear-fill me-2"></i>
                    Machines in Unit {unitName}
                </h5>
                <div className="list-group">
                    {machines.map((machine) => (
                        <Link
                            key={machine._id}
                            to={`/machine/${organizationId}/${unitId}/${machine._id}`}
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
            </div>
            <div className="card-footer text-muted">
                <small>Total Machines: {machines.length}</small>
            </div>
        </div>
    );
};

export default MachineList;
