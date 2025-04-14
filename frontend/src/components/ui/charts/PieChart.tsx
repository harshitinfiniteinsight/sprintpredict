
import React from "react";
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

interface PieChartProps {
  data: any[];
  index: string;
  categories?: string[];
  colors: string[];
  valueFormatter?: (value: number) => string;
}

const PieChart = ({
  data = [],
  index,
  colors,
  valueFormatter = (value) => `${value}`,
}: PieChartProps) => {
  // Simplified config
  const chartConfig = Array.isArray(data) 
    ? data.reduce((config, entry, i) => {
        return {
          ...config,
          [entry.name]: {
            color: colors[i % colors.length],
            label: entry.name,
          },
        };
      }, {}) 
    : {};

  // Simple empty state
  if (!Array.isArray(data) || data.length === 0) {
    return <div className="flex items-center justify-center h-full">No data available</div>;
  }

  return (
    <ChartContainer config={chartConfig}>
      <ResponsiveContainer width="100%" height={300}>
        <RechartsPieChart>
          <ChartTooltip
            content={
              <ChartTooltipContent
                labelFormatter={(value) => `${value}`}
                formatter={(value) => [valueFormatter(Number(value)), ""]}
              />
            }
          />
          <Legend layout="horizontal" verticalAlign="bottom" align="center" />
          <Pie
            data={data}
            cx="50%"
            cy="40%"
            labelLine={false}
            outerRadius={80}
            dataKey="value"
            nameKey={index}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
        </RechartsPieChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default PieChart;
