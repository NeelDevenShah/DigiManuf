import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { useState, useEffect } from 'react';


const OrganizationDashboard: React.FC<{ organizationId: string }> = ({ organizationId }) => {

    const [data, setData] = React.useState<any>({"unit":0, "machines":0, "sensors":0});

    useEffect(() => {
        let getData = async () => {
            // TODO: Change the URL to fetch units for the data based on the organizationId, so take the organizationId as a parameter
            let units = await fetch('http://localhost:3001/api/org/unit', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            // TODO: Change the URL to fetch units for the data based on the organizationId, so take the organizationId as a parameter
            let machines = await fetch('http://localhost:3001/api/org/machine', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            // TODO: Change the URL to fetch units for the data based on the organizationId, so take the organizationId as a parameter
            let sensors = await fetch('http://localhost:3001/api/org/sensor', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            let unitData = await units.json();
            let machineData = await machines.json();
            let sensorData = await sensors.json();

            setData({
                unit: unitData.data.length,
                machines: machineData.data.length,
                sensors: sensorData.data.length,
            });
        };
        getData();
    }, [data.sensors]);

    return (
        <div className="container mt-4">
            <div className="row">
                <div className="col-12">
                    <div className="card shadow-sm">
                        <div className="card-body">
                            <h2 className="card-title mb-4">
                                <i className="bi bi-building me-2"></i>
                                Organization Overview
                            </h2>
                            <div className="row">
                                <div className="col-md-4 mb-3">
                                    <div className="card bg-light">
                                        <div className="card-body text-center">
                                            <h5 className="card-title">
                                                <i className="bi bi-boxes me-2"></i>
                                                Total Units
                                            </h5>
                                            <p className="card-text display-4">{data.unit}</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-4 mb-3">
                                    <div className="card bg-light">
                                        <div className="card-body text-center">
                                            <h5 className="card-title">
                                                <i className="bi bi-gear me-2"></i>
                                                Total Machines
                                            </h5>
                                            <p className="card-text display-4">{data.machines}</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-4 mb-3">
                                    <div className="card bg-light">
                                        <div className="card-body text-center">
                                            <h5 className="card-title">
                                                <i className="bi bi-cpu me-2"></i>
                                                Total Sensors
                                            </h5>
                                            <p className="card-text display-4">{data.sensors}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OrganizationDashboard;