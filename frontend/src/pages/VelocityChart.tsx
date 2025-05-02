import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './VelocityChart.css';

const VelocityChartCard = () => {
    const [json1, setJson1] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/sprint/velocity-chart');
                setJson1(response.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []);

    if (!json1) {
        return <div>Loading...</div>;
    }

    const rawForecastedVelocityString = json1.forecasted_velocity;
    const dataArray = JSON.parse(rawForecastedVelocityString);

    const processedData = dataArray.map(item => ({
        start_date: new Date(item.start_date).getTime(),
        velocity: item.velocity,
        type: item.type
    }));

    processedData.sort((a, b) => a.start_date - b.start_date);

    const formattedDataForChart = processedData.map(item => ({
        ...item,
        start_date_formatted: new Date(item.start_date).toLocaleDateString()
    }));

    const colors = {
        'Historical Train Velocity': '#8884d8',
        'Historical Test Actual Velocity': '#82ca9d',
        'Historical Test Predicted Velocity': '#ffc658',
        'Forecasted Velocity': '#ff7300',
    };

    const dataTypes = [...new Set(formattedDataForChart.map(item => item.type as keyof typeof colors))];

    return (
        <div className="chart-card">
            <h3>Velocity Over Time</h3>
            <ResponsiveContainer width="100%" height={600}>
                <LineChart
                    data={formattedDataForChart}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="start_date"
                        scale="time"
                        type="number"
                        domain={[new Date('2023-01-01').getTime(), 'dataMax']}
                        tickFormatter={(unixTime) => new Date(unixTime).toLocaleDateString()}
                    />
                    <YAxis label={{ value: 'Velocity', angle: -90, position: 'insideLeft' }} />
                    <Tooltip labelFormatter={(unixTime) => new Date(unixTime).toLocaleDateString()} wrapperStyle={{ display: 'none' }} />
                    <Legend />

                    {dataTypes.map(type => {
                        const filteredData = formattedDataForChart.filter(item => item.type === type);
                        return (
                            <Line
                                key={type}
                                type="monotone"
                                dataKey="velocity"
                                stroke={colors[type] || '#000'}
                                name={type}
                                data={filteredData}
                                dot={false}
                            />
                        );
                    })}

                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default VelocityChartCard;