import React, { useState, useEffect } from "react";
import { format, addDays } from "date-fns";
import axios from "axios";

const LeaveCalendar = () => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [leaves, setLeaves] = useState([]);
  const [publicHolidays, setPublicHolidays] = useState([]);

  useEffect(() => {
    const fetchHolidaysAndLeaves = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/holidays-leaves");
        const { holidays, leaves } = response.data;

        setPublicHolidays(holidays.map((holiday) => ({ date: holiday.date, type: holiday.holidayName })));
        setLeaves(leaves);
      } catch (error) {
        console.error("Error fetching holidays and leaves:", error);
      }
    };

    fetchHolidaysAndLeaves();
  }, []);

  const handleAddLeave = (developer, date, type) => {
    if (type === "Leave") {
      setLeaves([...leaves, { developer, date }]);
    } else if (type === "Public Holiday") {
      setPublicHolidays([...publicHolidays, { date, type }]);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    return new Date(year, month + 1, 0).getDate();
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentMonth);
    const firstDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).getDay();
    const rows = [];
    let cells = [];

    for (let i = 0; i < firstDay; i++) {
      cells.push(<td key={`empty-${i}`} className="bg-gray-100">&nbsp;</td>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
      const formattedDate = format(date, "yyyy-MM-dd");
      const leaveInfo = leaves.filter((entry) => entry.date === formattedDate);
      const holidayInfo = publicHolidays.filter((entry) => entry.date === formattedDate);

      cells.push(
        <td
          key={day}
          className={`border p-2 align-top ${date.getDay() === 0 || date.getDay() === 6 ? 'bg-gray-200' : ''}`}
        >
          <div className="font-bold">{day}</div>
          {leaveInfo.map((info, index) => (
            <div
              key={`leave-${index}`}
              className="mt-1 px-2 py-1 rounded text-white text-xs bg-red-500"
            >
              {`${info.developer} on Leave`}
            </div>
          ))}
          {holidayInfo.map((info, index) => (
            <div
              key={`holiday-${index}`}
              className="mt-1 px-2 py-1 rounded text-white text-xs bg-blue-500"
            >
              {info.type}
            </div>
          ))}
        </td>
      );

      if ((day + firstDay) % 7 === 0 || day === daysInMonth) {
        rows.push(<tr key={`row-${day}`}>{cells}</tr>);
        cells = [];
      }
    }

    return rows;
  };

  return (
    <div className="p-6 bg-white shadow-lg rounded-lg border border-gray-200 w-full">
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={() => setCurrentMonth(addDays(currentMonth, -30))}
          className="px-4 py-2 bg-gray-200 rounded"
        >
          Previous
        </button>
        <span className="font-bold">
          {format(currentMonth, "MMMM yyyy")}
        </span>
        <button
          onClick={() => setCurrentMonth(addDays(currentMonth, 30))}
          className="px-4 py-2 bg-gray-200 rounded"
        >
          Next
        </button>
      </div>
      <table className="w-full border-collapse border border-gray-300 table-fixed">
        <thead>
          <tr>
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, index) => (
              <th
                key={day}
                className={`border p-2 bg-gray-100 w-1/7 ${index === 0 || index === 6 ? 'bg-gray-200' : ''}`}
              >
                {day}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{renderCalendar()}</tbody>
      </table>
      
    </div>
  );
};

export default LeaveCalendar;