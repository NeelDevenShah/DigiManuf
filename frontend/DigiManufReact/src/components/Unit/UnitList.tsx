import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

interface Unit {
    _id: string;
    name: string;
}

const UnitList: React.FC = () => {
    const [units, setUnits] = useState<Unit[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch units from API
    const getData = async () => {
        try {
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
            setUnits(data.data); // Assuming the response is an array of units
            setLoading(false);
        } catch (err: any) {
            setError(err.message || 'Something went wrong');
            setLoading(false);
        }
    };

    // Fetch units on component mount
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
                            {/* Conditional Rendering: Loading state */}
                            {loading && <p>Loading units...</p>}

                            {/* Conditional Rendering: Error state */}
                            {error && <p className="text-danger">{error}</p>}

                            {/* Conditional Rendering: Empty state */}
                            {!loading && !error && units.length === 0 && <p>No units available.</p>}

                            {/* Render unit list if data is available */}
                            {!loading && !error && units.length > 0 && (
                                <ul className="list-group list-group-flush">
                                    {units.map((unit) => (
                                        <li key={unit._id} className="list-group-item p-0">
                                            <Link
                                                to={`/unit/${unit._id}`}
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
