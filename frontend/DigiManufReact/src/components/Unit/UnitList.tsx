import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

interface Unit {
    _id: string;
    name: string;
}

const UnitList: React.FC<{ organizationId: string }> = ({ organizationId }) => {
    const [units, setUnits] = useState<Unit[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch units from API
    const getData = async () => {
        try {
            // TODO: Change the URL to fetch data for the organization based on the organizationId, so take the organizationId as a parameter
            const response = await fetch('http://localhost:3001/api/org/unit', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch units');
            }

            const data = await response.json();
            setUnits(data.data);
            setLoading(false);
        } catch (err: any) {
            setError(err.message || 'Something went wrong');
            setLoading(false);
        }
    };

    useEffect(() => {
        getData();
    }, []);

    return (
        <div className="container my-5">
            <div className="row justify-content-center">
                <div className="col-md-8 col-lg-6">
                    <div className="card shadow-sm">
                        <h2 className="card-header text-center bg-primary text-white">
                            <i className="bi bi-list-ul me-2"></i>Unit List
                        </h2>
                        <div className="card-body">
                            {loading && <p>Loading units...</p>}

                            {error && <p className="text-danger">{error}</p>}

                            {!loading && !error && units.length === 0 && <p>No units available.</p>}

                            {!loading && !error && units.length > 0 && (
                                <ul className="list-group list-group-flush">
                                    {units.map((unit) => (
                                        <li key={unit._id} className="list-group-item p-0">
                                            <Link
                                                to={`/unit/${organizationId}/${unit._id}`}
                                                className="d-flex justify-content-between align-items-center p-3 text-decoration-none text-dark"
                                            >
                                                <span>
                                                    <i className="bi bi-book me-2 text-primary"></i>
                                                    {unit.name}
                                                </span>
                                                <i className="bi bi-chevron-right text-primary"></i>
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UnitList;
