import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './VelocityChart.css';

const VelocityChartCard = ({ jsonData }) => {
    const json1={
        "forecasted_velocity": "[{\"start_date\":\"2023-01-15\",\"velocity\":33.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-01-29\",\"velocity\":20.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-02-12\",\"velocity\":31.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-02-26\",\"velocity\":21.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-03-12\",\"velocity\":23.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-03-26\",\"velocity\":34.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-04-09\",\"velocity\":34.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-04-23\",\"velocity\":40.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-05-07\",\"velocity\":17.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-05-21\",\"velocity\":36.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-06-04\",\"velocity\":41.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-06-18\",\"velocity\":30.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-07-02\",\"velocity\":42.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-07-16\",\"velocity\":17.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-07-30\",\"velocity\":26.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-08-13\",\"velocity\":12.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-08-27\",\"velocity\":21.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-09-10\",\"velocity\":30.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-09-24\",\"velocity\":26.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-10-08\",\"velocity\":24.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-10-22\",\"velocity\":38.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-11-05\",\"velocity\":21.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-11-19\",\"velocity\":36.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-12-03\",\"velocity\":34.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-12-17\",\"velocity\":30.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2023-12-31\",\"velocity\":28.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-01-14\",\"velocity\":30.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-01-28\",\"velocity\":43.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-02-11\",\"velocity\":21.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-02-25\",\"velocity\":15.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-03-10\",\"velocity\":41.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-03-24\",\"velocity\":28.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-04-07\",\"velocity\":30.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-04-21\",\"velocity\":37.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-05-05\",\"velocity\":37.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-05-19\",\"velocity\":43.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-06-02\",\"velocity\":34.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-06-16\",\"velocity\":44.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-06-30\",\"velocity\":14.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-07-14\",\"velocity\":22.0,\"type\":\"Historical Train Velocity\"},{\"start_date\":\"2024-07-28\",\"velocity\":21.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-07-28\",\"velocity\":17.5412797619,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-08-11\",\"velocity\":42.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-08-11\",\"velocity\":32.7184305556,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-08-25\",\"velocity\":41.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-08-25\",\"velocity\":38.0795277778,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-09-08\",\"velocity\":27.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-09-08\",\"velocity\":28.1923407287,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-09-22\",\"velocity\":23.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-09-22\",\"velocity\":28.4930928932,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-10-06\",\"velocity\":29.1223071789,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-10-06\",\"velocity\":24.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-10-20\",\"velocity\":35.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-10-20\",\"velocity\":37.2655674603,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-11-03\",\"velocity\":34.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-11-03\",\"velocity\":30.9795218254,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-11-17\",\"velocity\":23.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-11-17\",\"velocity\":29.1560093795,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-12-01\",\"velocity\":24.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-12-01\",\"velocity\":30.7524058442,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-12-15\",\"velocity\":19.0,\"type\":\"Historical Test Actual Velocity\"},{\"start_date\":\"2024-12-15\",\"velocity\":24.9859951299,\"type\":\"Historical Test Predicted Velocity\"},{\"start_date\":\"2024-12-29\",\"velocity\":27.3767635281,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-01-12\",\"velocity\":31.0426082251,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-01-26\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-02-09\",\"velocity\":28.7245308442,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-02-23\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-03-09\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-03-23\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-04-06\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-04-20\",\"velocity\":28.7245308442,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-05-04\",\"velocity\":28.7245308442,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-05-18\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-06-01\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-06-15\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-06-29\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-07-13\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-07-27\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-08-10\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-08-24\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-09-07\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-09-21\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-10-05\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-10-19\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-11-02\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-11-16\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-11-30\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-12-14\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2025-12-28\",\"velocity\":28.7245308442,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-01-11\",\"velocity\":28.7245308442,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-01-25\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-02-08\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-02-22\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-03-08\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-03-22\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-04-05\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-04-19\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-05-03\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-05-17\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-05-31\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-06-14\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-06-28\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-07-12\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-07-26\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-08-09\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-08-23\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-09-06\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-09-20\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-10-04\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-10-18\",\"velocity\":31.2425248918,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-11-01\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-11-15\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-11-29\",\"velocity\":31.5833542569,\"type\":\"Forecasted Velocity\"},{\"start_date\":\"2026-12-13\",\"velocity\":28.9540744949,\"type\":\"Forecasted Velocity\"}]"
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