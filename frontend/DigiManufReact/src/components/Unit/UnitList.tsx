import React from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

interface Unit {
    id: string;
    name: string;
}

const UnitList: React.FC = () => {
    // Fetch units from API or state management
    const units: Unit[] = [
        { id: '1', name: 'Unit 1' },
        { id: '2', name: 'Unit 2' },
    ];

    return (
        // Added container for responsive layout
        <div className="container my-5">
            {/* Added row and column for grid system */}
            <div className="row justify-content-center">
                <div className="col-md-8 col-lg-6">
                    {/* Wrapped content in a card for better visual appeal */}
                    <div className="card shadow-sm">
                        <h2 className="card-header text-center bg-primary text-white">
                            <i className="bi bi-list-ul me-2"></i>Unit List
                        </h2>
                        {/* Used list-group for a clean, interactive list */}
                        <ul className="list-group list-group-flush">
                            {units.map((unit) => (
                                <li key={unit.id} className="list-group-item p-0">
                                    <Link 
                                        to={`/unit/${unit.id}`}
                                        className="d-flex justify-content-between align-items-center p-3 text-decoration-none text-dark"
                                    >
                                        <span>
                                            <i className="bi bi-book me-2 text-primary"></i>
                                            {unit.name}
                                        </span>
                                        {/* Added an icon for visual enhancement */}
                                        <i className="bi bi-chevron-right text-primary"></i>
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UnitList;