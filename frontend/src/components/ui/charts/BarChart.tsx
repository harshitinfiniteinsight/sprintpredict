
import React from "react";
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

interface BarChartProps {
  data: any[];
  index: string;
  categories: string[];
  colors: string[];
  valueFormatter?: (value: number) => string;
  yAxisWidth?: number;
}

const BarChart = ({
  data = [],
  index,
  categories = [],
  colors = [],
  valueFormatter = (value) => `${value}`,
  yAxisWidth = 56,
}: BarChartProps) => {
  // Simplified config
  const chartConfig = (categories || []).reduce((config, category, i) => {
    return {
      ...config,
      [category]: {
        color: colors[i % colors.length] || "#888",
      },
    };
  }, {});

  // Simple empty state
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-full">No data available</div>;
  }

  return (
    <ChartContainer config={chartConfig}>
      <ResponsiveContainer width="100%" height={300}>
        <RechartsBarChart 
          data={data} 
          margin={{ top: 10, right: 10, left: 10, bottom: 24 }}
          layout="vertical"
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis
            type="number"
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 12 }}
            tickFormatter={valueFormatter}
          />
          <YAxis
            type="category"
            dataKey={index}
            tickLine={false}
            axisLine={false}
            width={yAxisWidth}
            tick={{ fontSize: 12 }}
          />
          <ChartTooltip
            content={
              <ChartTooltipContent
                labelFormatter={(value) => `${value}`}
                formatter={(value) => [valueFormatter(Number(value)), ""]}
              />
            }
          />
          {categories.map((category, i) => (
            <Bar
              key={category}
              dataKey={category}
              fill={colors[i % colors.length]}
              radius={4}
              barSize={20}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default BarChart;
