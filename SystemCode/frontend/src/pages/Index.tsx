import React, { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/components/ui/use-toast";
//import { TableContainer, Table, TableHead, TableRow, TableCell, TableBody, Paper } from "@mui/material";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar } from "@/components/ui/calendar";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, Users, Activity, Gift, Calendar as CalendarIcon, CheckCircle2, Clock, AlertTriangle, Award, TrendingUp, ChevronRight, History, Filter, LineChart, BarChart as BarChartIcon, PieChart as PieChartIcon, Download, Search, ArrowUp, ArrowDown, List, Layers, Maximize, Check } from "lucide-react";
import { teamData1, sprintHistory,dummyBacklog1, sprintSummary, chartConfig, velocityData, burndownData } from "@/data/dummyData";
import BarChart from "@/components/ui/charts/BarChart";
import PieChart from "@/components/ui/charts/PieChart";
import SprintChatbot from "@/components/SprintChatbot";
import { format, addDays, isWeekend } from "date-fns";
import { Link, Route, Routes } from "react-router-dom";
import TeamData from "./TeamData";
import ProductBacklog from "./ProductBacklog";
import SprintHistory from "./SprintHistory";
import VelocityChart from "./VelocityChart";

const extendedChartConfig = {
  ...chartConfig,
  points: {
    data: dummyBacklog1.slice(0, 5).map(item => ({
      name: item.type,
      value: item.points
    })),
    index: "name",
    categories: ["value"],
    colors: ["#8B5CF6", "#D946EF", "#F97316", "#0EA5E9"],
    valueFormatter: (value: number) => `${value} pts`
  },
  projectedBurndown: {
    data: burndownData,
    index: "day",
    categories: ["remaining", "ideal"],
    colors: ["#8B5CF6", "#D3D3D3"],
    valueFormatter: (value: number) => `${value} pts`
  },
  allocation: {
    data: teamData1.slice(0, 5).map(member => ({
      name: member.name.split(" ")[0],
      value: member.capacity
    })),
    index: "name",
    categories: ["value"],
    colors: ["#8B5CF6", "#D946EF", "#F97316", "#0EA5E9", "#10B981"],
    valueFormatter: (value: number) => `${value} pts`
  },
  capacity: {
    data: teamData1.map(member => ({
      name: member.name,
      value: member.capacity
    })),
    index: "name",
    categories: ["value"],
    colors: ["#8B5CF6", "#D946EF", "#F97316", "#0EA5E9", "#10B981"],
    valueFormatter: (value: number) => `${value} pts`
  }
};

const getWorkingDays = (startDate, endDate) => {
  const workingDays = [];
  let currentDate = new Date(startDate);
  while (currentDate <= new Date(endDate)) {
    if (!isWeekend(currentDate)) {
      workingDays.push(new Date(currentDate));
    }
    currentDate = addDays(currentDate, 1);
  }
  return workingDays;
};

const taskColors = {};
const getTaskColor = (task) => {
  if (!taskColors[task]) {
    const colorPalette = ["bg-red-200", "bg-blue-200", "bg-green-200", "bg-yellow-200", "bg-purple-200", "bg-pink-200", "bg-teal-200", "bg-orange-200"];
    const colorIndex = Object.keys(taskColors).length % colorPalette.length;
    taskColors[task] = colorPalette[colorIndex];
  }
  return taskColors[task];
};

const evaluateHolidaysAndLeaves = (holidayLeaveData, startDate, endDate) => {
  const start = new Date(startDate);
  const end = new Date(endDate);

  const publicHolidays = holidayLeaveData.holidays.filter(holiday => {
      const holidayDate = new Date(holiday.date);
      return holidayDate >= start && holidayDate <= end;
  }).length;

  const totalLeaves = holidayLeaveData.leaves.filter(leave => {
      const leaveDate = new Date(leave.date);
      return leaveDate >= start && leaveDate <= end;
  }).length;

  return { publicHolidays, totalLeaves };
};

const TaskAssignmentTable = ({ developers, startDate, endDate, sprintAssignment }) => {
  const workingDays = getWorkingDays(startDate, endDate);
  console.log("Working Days:", workingDays);

  const [holidayLeaveData, setHolidayLeaveData] = React.useState({});

  React.useEffect(() => {
    const fetchHolidayLeaveData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/holidays-leaves");
        console.log("Holiday and leave data fetched:", response.data);
        setHolidayLeaveData(response.data);
      } catch (error) {
        console.error("Error fetching holiday and leave data:", error);
      }
    };

    fetchHolidayLeaveData();
  }, []);

  const dummyAssignments = React.useMemo(() => {
    const assignments = {};

    // Assign holidays and leaves
    Object.entries(holidayLeaveData).forEach(([date, dataArray]) => {
      console.log("Processing holiday/leave date:", date);
      console.log("Processing holiday/leave data:", dataArray);
      dataArray.forEach((data) => {
      developers.forEach((developer) => {
        
        if (!assignments[developer.name]) {
          assignments[developer.name] = {};
        }
        if (!assignments[developer.name][data.date]) {
          assignments[developer.name][data.date] = [];
        }

        if (date === "holidays") {
          assignments[developer.name][data.date].push({
            task: data.holidayName,
            points: "na",
            color: "bg-blue-400",
          });
        } else if (date === "leaves" && data.developer === developer.name) {
          assignments[developer.name][data.date].push({
            task: "Leave",
            points: "na",
            color: "bg-red-400",
          });
        }
      });
    });
    });

    console.log("Dummy Assignments before recalculation:", assignments);

    console.log("Recalculating TaskAssignmentTable with sprintAssignment:", sprintAssignment);
    Object.entries(sprintAssignment || {}).forEach(([developer, data]) => {
      if (data) {
        Object.entries(data).forEach(([date, tasks]) => {
          tasks.forEach((taskEntry) => {
            if (!assignments[developer]) {
              assignments[developer] = {};
            }
            if (!assignments[developer][date]) {
              assignments[developer][date] = [];
            }
            assignments[developer][date].push({
              task: taskEntry.task,
              points: taskEntry.points,
            });
          });
        });
      }
    });
    return assignments;
  }, [sprintAssignment, holidayLeaveData]);

  console.log("Dummy Assignments after recalculation:", dummyAssignments);

  const renderTaskBlocks = (developerName, day, task) => {
    const isContinuation = workingDays.some((prevDay) => {
      const prevDate = format(prevDay, "yyyy-MM-dd");
      return dummyAssignments[developerName]?.[prevDate]?.some(t => t.task === task.task);
    });

    const truncatedTask = task.task.length > 15 ? `${task.task.slice(0, 15)}...` : task.task;

    return (
      <div
        className={`${task.color || getTaskColor(task.task)} text-black p-1 rounded text-center whitespace-nowrap ${isContinuation ? "rounded-l-none" : ""}`}
        title={`Task: ${task.task}\n${task.points !== 'na' ? `Points: ${task.points}\n` : ''}Developer: ${developerName}`}
      >
        <div>{truncatedTask}</div>
        {task.points !== 'na' && <div className="text-xs">{task.points} pts</div>}
      </div>
    );
  };

  return (
    <div className="overflow-auto" style={{ maxHeight: "800px" }}>
  <Table>
    <TableHeader>
      <TableRow className="sticky top-0 bg-white z-10">
        {/* Sticky Developer Column Header */}
        <TableHead className="sticky top-0 left-0 bg-white z-20">Developer</TableHead>
        {workingDays.map((day, index) => (
          <TableHead key={index} className="sticky top-0 bg-white z-10">
            {format(day, "dd MMM")}
          </TableHead>
        ))}
      </TableRow>
    </TableHeader>
    <TableBody>
      {developers.map((developer) => (
        <TableRow key={developer.name}>
          {/* Sticky Developer Column */}
          <TableCell className="sticky left-0 bg-white z-10">{developer.name}</TableCell>
          {workingDays.map((day, index) => (
            <TableCell key={index}>
              {dummyAssignments[developer.name]?.[format(day, "yyyy-MM-dd")] ? (
                <div className="flex flex-col gap-1">
                  {dummyAssignments[developer.name][format(day, "yyyy-MM-dd")].map((task, taskIndex) =>
                    renderTaskBlocks(developer.name, day, task)
                  )}
                </div>
              ) : (
                "-"
              )}
            </TableCell>
          ))}
        </TableRow>
      ))}
    </TableBody>
  </Table>
</div>
   
  );
};

const LeaveCalendar = () => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [leaveData, setLeaveData] = useState([
    { developer: "Alice", date: "2025-04-27", type: "Leave" },
    { developer: "Bob", date: "2025-04-28", type: "Public Holiday" },
    { developer: "Charlie", date: "2025-04-30", type: "Leave" },
    { developer: "Charlie", date: "2025-04-10", type: "Leave" },
    { developer: "Bob", date: "2025-04-10", type: "Leave" },
  ]);

  const handleAddLeave = (developer, date, type) => {
    setLeaveData([...leaveData, { developer, date, type }]);
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
      const leaveInfo = leaveData.filter((entry) => entry.date === formattedDate);

      cells.push(
        <td key={day} className="border p-2 align-top">
          <div className="font-bold">{day}</div>
          {leaveInfo.map((info, index) => (
            <div
              key={index}
              className={`mt-1 px-2 py-1 rounded text-white text-xs ${
                info.type === "Leave" ? "bg-red-500" : "bg-blue-500"
              }`}
            >
              {info.type === "Leave" ? `${info.developer} on Leave` : info.type}
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
      <h3 className="text-2xl font-bold mb-6 text-center text-secondary">Leave & Public Holiday Calendar</h3>
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
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
              <th key={day} className="border p-2 bg-gray-100 w-1/7">
                {day}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{renderCalendar()}</tbody>
      </table>
      <div className="mt-6">
        <h4 className="text-lg font-bold mb-2">Add Leave/Public Holiday</h4>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const developer = formData.get("developer");
            const date = formData.get("date");
            const type = formData.get("type");
            handleAddLeave(developer, date, type);
          }}
          className="flex flex-col gap-2"
        >
          <input
            type="text"
            name="developer"
            placeholder="Developer Name"
            className="border p-2 rounded"
            required
          />
          <input
            type="date"
            name="date"
            className="border p-2 rounded"
            required
          />
          <select name="type" className="border p-2 rounded" required>
            <option value="Leave">Leave</option>
            <option value="Public Holiday">Public Holiday</option>
          </select>
          <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">
            Add
          </button>
        </form>
      </div>
    </div>
  );
};

const NavigationSidebar = () => {
  const navigationItems = [
    { name: "Home", link: "#" },
    { name: "Sprint Data", link: "#" },
  ];

  return (
    <div className="w-64 h-screen bg-[hsl(var(--accent))] text-gray-300 fixed top-0 left-0 shadow-lg">
      <div className="p-4 text-lg font-bold glow-text border-b border-gray-700">SprintPredict1</div>
      <ul className="mt-4">
        {navigationItems.map((item, index) => (
          <li key={index} className="p-4 hover:bg-gray-700 cursor-pointer transition-all duration-300">
            <a href={item.link} className="hover:text-white">{item.name}</a>
          </li>
        ))}
      </ul>
    </div>
  );
};

const SprintPlanningDashboard = ({ activePage }) => {
  const [activeTab, setActiveTab] = useState("upload");
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedTask, setExpandedTask] = useState<string | null>(null);
  const [currentSprintId, setCurrentSprintId] = useState<string>("sprint-7");
  const [sprints, setSprints] = useState([{
    id: "sprint-7",
    name: "Sprint 7",
    goal: "Complete user authentication and profile features",
    startDate: "April 5, 2025",
    endDate: "April 18, 2025",
    duration: 14,
    status: "Planning",
    totalPoints: 85,
    totalTasks: 7,
    teamMembers: 7
  }]);
  const [dummyBacklog, setDummyBacklog] = useState([]);

  useEffect(() => {
    const fetchBacklog = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/backlog/tasks");
        console.log("Backlog data fetched:", response.data);
        setDummyBacklog(response.data.tasks);
      } catch (error) {
        console.error("Error fetching backlog data:", error);
      }
    };

    fetchBacklog();
  }, []);

  const [teamData, setTeamData] = useState([]);

  useEffect(() => {
    const fetchTeamData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/team/members");
        console.log("Team data fetched:", response.data);
        setTeamData(response.data.members);
      } catch (error) {
        console.error("Error fetching team data:", error);
      }
    };

    fetchTeamData();
  }, []);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    /*toast({
      title: "Section Changed",
      description: `Moved to ${value} section`
    });*/
  };
  const downloadDummyFile = (fileType: string) => {
    toast({
      title: "Download Started",
      description: `Downloading ${fileType} template...`
    });
  };
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      toast({
        title: "File Uploaded",
        description: `${e.target.files[0].name} has been uploaded successfully!`
      });
    }
  };
  const [sprintAssignment, setSprintAssignment] = useState([]);
  const [totalStoryPoint, setTotalStoryPoint] = useState([]);
  const [totalTasks, setTotalTasks] = useState([]);
  const [riskCategory, setRiskCategory] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const generatePlan = async () => {
    setIsLoading(true); // Show loader before API call
    try {
      const response = await axios.get("http://localhost:8000/api/sprint/task-distribution-new");
      console.log("Sprint assignment data:", response.data.optimization_summary.developer_daily_schedule);
      setSprintAssignment(response.data.optimization_summary.developer_daily_schedule);
      setTotalTasks(response.data.optimization_summary.total_tasks_selected);
      setTotalStoryPoint(response.data.optimization_summary.total_story_points_selected);
      console.log("Total Story Points:", response.data.optimization_summary);
      setRiskCategory(categorizeSprintPlan(totalStoryPoint,forecastedVelocity))
      setActiveTab("results");
      /*toast({
        title: "Sprint Plan Generated",
        description: "AI has generated the optimal sprint plan based on the provided data."
      });*/
    } catch (error) {
      console.error("Error syncing from JIRA:", error);
      toast({
        title: "Sync Failed",
        description: "Could not refresh Product Backlog from JIRA.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false); // Hide loader after API call completes
    }
};

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "3":
        return <Badge className="bg-orange-500">High</Badge>;
      case "2":
        return <Badge className="bg-blue-500">Medium</Badge>;
      case "1":
        return <Badge className="bg-purple-500">Low</Badge>;
      default:
        return <Badge>{priority}</Badge>;
    }
  };
  const filteredBacklog = dummyBacklog.filter(task => task.issue_key.toLowerCase().includes(searchTerm.toLowerCase()) || task.summary.toLowerCase().includes(searchTerm.toLowerCase()) || task.assigned.toLowerCase().includes(searchTerm.toLowerCase()) || task.skills.toLowerCase().includes(searchTerm.toLowerCase()));
  const getCompletionRate = (completed: number, planned: number) => {
    return Math.round(completed / planned * 100);
  };
  const createNewSprint = () => {
    const newSprintNumber = sprints.length + 7; // Starting from Sprint 7
    const newSprint = {
      id: `sprint-${newSprintNumber}`,
      name: `Sprint ${newSprintNumber}`,
      goal: "New sprint goal",
      startDate: "TBD",
      endDate: "TBD",
      duration: 14,
      status: "Planning",
      totalPoints: 0,
      totalTasks: 0,
      teamMembers: 7
    };
    setSprints([...sprints, newSprint]);
    setCurrentSprintId(newSprint.id);
    toast({
      title: "New Sprint Created",
      description: `${newSprint.name} has been created and is ready for planning.`
    });
  };
  const getCurrentSprint = () => {
    return sprints.find(s => s.id === currentSprintId) || sprints[0];
  };

  const handleSyncFromJIRA = async () => {
    try {
      const response1 = await axios.get("http://localhost:8000/api/sync/jira");
      const response = await axios.get("http://localhost:8000/api/backlog/tasks");
      setDummyBacklog(response.data.tasks);
      toast({
        title: "Sync Successful",
        description: "Product Backlog has been refreshed from JIRA."
      });
    } catch (error) {
      console.error("Error syncing from JIRA:", error);
      toast({
        title: "Sync Failed",
        description: "Could not refresh Product Backlog from JIRA.",
        variant: "destructive"
      });
    }
  };

  const handleMenuClick = (menu) => {
    setActiveTab(menu);
  };

  const handleApprovePlan = async () => {
    setIsLoading(true); // Show loader
  
    
    const sanitizedSprintName = currentSprintName.replace(/^Sprint \s*/, "");
    const requestBody = {
      sprint_number: sanitizedSprintName,
      start_date: currentSprintStart,
      end_date: currentSprintEnd,
      team_size: 5,
      committed_story_points: totalStoryPoint,
      completed_story_points: 0, 
      planned_leave_days_team: 2, 
      unplanned_leave_days_team: 1, 
      major_impediment: 0,
      backlog_well_refined_percentage: 72, 
      sprint_duration_days: 14, // Assuming 14 days
      available_person_days: 10,
      lagged_velocity: 250, // Placeholder value
      status: "In Progress",
    };

    console.log("Request Body for Approval:", requestBody);
  
    try {
      await axios.post("http://localhost:8000/api/sprint/history", requestBody);
      toast({
        title: "Plan Approved",
        description: "Sprint plan has been successfully approved and saved to history.",
      });
  
      setTimeout(() => {
        setActivePage("sprint-history"); // Switch to Sprint History page
      }, 1000);
    } catch (error) {
      console.error("Error approving plan:", error);
      toast({
        title: "Approval Failed",
        description: "Could not approve the sprint plan. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false); // Hide loader
    }
  };

  const setActivePage = (page: string) => {
    if (page === "sprint-history") {
      window.location.href = "http://localhost:8080/sprint-history";
    }
  };

  const [previousSprintName, setPreviousSprintName] = useState("");
  const [currentSprintName, setCurrentSprintName] = useState("");
  const [currentSprintStart, setCurrentSprintStart] = useState("");
  const [currentSprintEnd, setCurrentSprintEnd] = useState("");
  const [sprintHistoryList, setSprintHistoryList]=useState([]);

  useEffect(() => {
    const fetchPreviousSprint = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/sprint/history");
        //const sortedSprints = response.data.sort((a, b) => new Date(b.endDate) - new Date(a.endDate));
        const sortedSprints = response.data.history.sort((a, b) => b.sprint_number - a.sprint_number); // Sort in descending order
        console.log("Previous sprint data fetched:", sortedSprints);
        if (sortedSprints.length > 0) {
          setPreviousSprintName("Sprint "+sortedSprints[0].sprint_number);
          setCurrentSprintName("Sprint "+(sortedSprints[0].sprint_number+1));
          setCurrentSprintStart(addDays(new Date(sortedSprints[0].end_date), 1).toISOString().split('T')[0]);
          setCurrentSprintEnd(addDays(new Date(sortedSprints[0].end_date), 14).toISOString().split('T')[0]);
          setSprintHistoryList(sortedSprints);
          
          
          console.log("Current Sprint Start Date:", sortedSprints[0].end_date);
        }
      } catch (error) {
        console.error("Error fetching previous sprint data:", error);
      }
    };

    fetchPreviousSprint();
  }, []);

  const formatDateForInput = (dateString) => {
    // Assuming the input dateString is already in the format 'YYYY-MM-DD'
    return dateString;
  };

  const formattedSprintStartDate = formatDateForInput(currentSprintStart);

  const calculateEndDate = (startDate, duration) => {
    const endDate = new Date(startDate);
    console.log("Start Date:", startDate);
    endDate.setDate(endDate.getDate() + duration);
    console.log("End Date:", endDate);
    return endDate;
  };

  // Ensure currentSprintStart is parsed correctly as a Date object
const [highlightedRange, setHighlightedRange] = useState<{ from?: Date; to?: Date }>(() => {
  
  const startDate = new Date();
  if (isNaN(startDate.getTime())) {
    console.error("Invalid date format for currentSprintStart. Expected format: YYYY-MM-DD");
    return { from: undefined, to: undefined };
  }
  console.log("Current Sprint Start Date111:", startDate);
  console.log("Highlighted Range1:", { from: startDate, to: calculateEndDate(startDate, 14)});
  return { from: startDate, to: calculateEndDate(startDate, 14) };
  
});

useEffect(() => {
  //if (currentSprintStartDate) {
    const startDate = new Date();
    console.log("Current Sprint Start Date333:", startDate);
    setHighlightedRange({ from: startDate, to: calculateEndDate(startDate, 14) });
    console.log("Highlighted Range:", { from: startDate, to: calculateEndDate(startDate, 14) });
  
}, [currentSprintStart]);

  const handleDateChange = (selectedDate, duration = 14) => {
    setDate(selectedDate);
    const newEndDate = calculateEndDate(selectedDate, duration); // Use the provided duration value 
    setHighlightedRange({ from: selectedDate, to: newEndDate });
};

const handleSprintDurationChange = (e) => {
    const newDuration = parseInt(e.target.value, 10) || 14; // Default to 14 if input is invalid
    handleDateChange(date, newDuration);
};

const [forecastedVelocity, setForecastedVelocity] = useState("");

useEffect(() => {
  const fetchForecastedVelocity = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/sprint/velocity-chart");
      const forecastedData = JSON.parse(response.data.forecasted_velocity);
      const currentDate = new Date();

      // Find the closest forecasted velocity to the current date or a future date
      const closestForecast = forecastedData
        .filter(item => new Date(item.start_date) >= currentDate)
        .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))[0];

      if (closestForecast) {
        console.log("Forecasted Velocity:", closestForecast);
        setForecastedVelocity(Math.ceil(closestForecast.velocity));
      }
    } catch (error) {
      console.error("Error fetching forecasted velocity:", error);
    }
  };

  fetchForecastedVelocity();
}, []);

function categorizeSprintPlan(forecastedVelocity, totalStoryPoints) {
  forecastedVelocity = Math.ceil(forecastedVelocity); // Convert forecastedVelocity to an integer
  const differencePercentage = ((totalStoryPoints - forecastedVelocity) / forecastedVelocity) * 100;

  if (differencePercentage >= 20) {
    return "Overcommitted / High Risk";
  } else if (differencePercentage > 5 && differencePercentage < 20) {
    return "Ambitious / Stretch";
  } else if (differencePercentage >= -5 && differencePercentage <= 5) {
    return "Realistic / On Track";
  } else if (differencePercentage < -5 && differencePercentage > -20) {
    return "Conservative / Under-planned";
  } else if (differencePercentage <= -20) {
    return "Significantly Under-planned";
  }
}

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary/30 via-background to-background">
      {/* Main content */}
      <div className="min-h-screen bg-gradient-to-br from-secondary/30 via-background to-background">
        <header className="bg-gradient-to-r from-primary to-accent p-1 text-white relative overflow-hidden">
          <div className="absolute inset-0 bg-grid-white/10 animate-pulse"></div>
          <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-gradient-to-br from-white/10 to-transparent rounded-full blur-2xl"></div>
          <div className="container mx-auto relative z-10">
            <div className="flex items-center justify-between">
              <h1 className="text-3xl font-bold mb-0 flex items-center">
                <Award className="mr-2" /> SprintPredict
              </h1>
              <div className="flex items-center space-x-3">
                
              </div>
            </div>
            <p className="text-white/80 max-w-xl">Plan, prioritize, and predict your sprint outcomes</p>
            
            {/* <div className="flex flex-wrap gap-3 mt-4">
              <Badge className="bg-white/20 hover:bg-white/30 transition-colors">AI-Powered</Badge>
              <Badge className="bg-white/20 hover:bg-white/30 transition-colors">Machine Learning</Badge>
              <Badge className="bg-white/20 hover:bg-white/30 transition-colors">Team Optimization</Badge>
              <Badge className="bg-white/20 hover:bg-white/30 transition-colors">Resource Planning</Badge>
            </div> */}
          </div>
          
        </header>

        <div className="flex w-full">
          {/* Left Navigation Bar */}
          <nav className="w-1/6 bg-card p-4 rounded-lg shadow-lg">
            <ul className="space-y-4">
              <li>
                <Link to="/" className="w-full text-left p-2 rounded-lg hover:bg-primary/10">Dashboard</Link>
              </li>
              <li>
                <Link to="/team-data" className="w-full text-left p-2 rounded-lg hover:bg-primary/10">Team Data</Link>
              </li>
              <li>
                <Link to="/product-backlog" className="w-full text-left p-2 rounded-lg hover:bg-primary/10">Product Backlog</Link>
              </li>
              <li>
                <Link to="/sprint-history" className="w-full text-left p-2 rounded-lg hover:bg-primary/10">Sprint History</Link>
              </li>
              <li>
                <Link to="/new-sprint" className="w-full text-left p-2 rounded-lg hover:bg-primary/10">New Sprint Plan</Link>
              </li>
            </ul>
          </nav>

          {/* Main Content Area */}
          <main className="w-4/5 py-8 px-4">
          
          {(() => {
              switch (activePage) {
                case "team-data":
                  return <TeamData teamData={teamData} />;
                case "product-backlog":
                  return <ProductBacklog dummyBacklog={dummyBacklog} />;
                case "sprint-history":
                  return <SprintHistory teamData={teamData}  />;
                case "dashboard":
                    return <VelocityChart chartData={teamData}  />;
                default:
                  return (
              <>
                <div className="mb-8 flex flex-col md:flex-row items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold gradient-text">Sprint Planning Dashboard</h2>
                    
                  </div>
                  
                  <div className="flex items-center mt-4 md:mt-0 space-x-2 bg-card p-3 rounded-lg shadow-lg border border-primary/20">
                    <CalendarIcon className="text-primary" size={20} />
                    <span>Today: {new Date().toLocaleDateString()}</span>
                    
                  </div>
                </div>

                


                <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
                  <TabsList className="grid grid-cols-5 mb-8 bg-card p-1 rounded-xl shadow-md">
                    <TabsTrigger value="upload" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
                      <Award size={18} /> New Sprint
                    </TabsTrigger>
                   
                    
                    <TabsTrigger value="results" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
                      <Activity size={18} /> Results
                    </TabsTrigger>
                    <TabsTrigger value="insights" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
                      <TrendingUp size={18} /> Insights
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="upload">
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-8">
                      

                      <Card className="md:col-span-1 border-t-4 border-t-secondary shadow-lg hover:shadow-xl transition-shadow">
                        
                        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
                          <div className="space-y-2">
                            <Label htmlFor="sprint-name" className="flex items-center">
                              <Award className="h-4 w-4 mr-2 text-secondary" /> Sprint Name
                            </Label>
                            <Input id="sprint-name" defaultValue={currentSprintName} className="border-secondary/20 focus:border-secondary" />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="sprint-start-date" className="flex items-center">
                              <CalendarIcon className="h-4 w-4 mr-2 text-accent" /> Sprint Start Date
                            </Label>
                            <Input id="sprint-start-date" type="date" defaultValue={formattedSprintStartDate} className="border-accent/20 focus:border-accent" />
                          </div>
                          
                          <div className="space-y-2">
                            <Label className="flex items-center">
                              <CalendarIcon className="h-4 w-4 mr-2 text-accent" /> Sprint Calendar
                            </Label>
                            <div className="border rounded-md p-2 bg-card">
                              <Calendar
                                mode="range"
                                selected={highlightedRange}
                                onSelect={(range) => {
                                  if (range?.start) handleDateChange(range.start);
                                }}
                                className="rounded-md"
                              />
                            </div>
                          </div>
                          <div className="space-y-4">
                            <div className="space-y-2">
                              <Label htmlFor="sprint-duration" className="flex items-center">
                                <Clock className="h-4 w-4 mr-2 text-accent" /> Sprint Duration (days)
                              </Label>
                              <Input id="sprint-duration" type="number" defaultValue="14" className="border-accent/20 focus:border-accent" onChange={handleSprintDurationChange} />
                            </div>
                            
                            <Button className="mt-4 w-full bg-gradient-to-r from-primary to-accent hover:opacity-90 pulse-primary" onClick={generatePlan}>
                              Generate Sprint Plan <ChevronRight className="ml-1" size={16} />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="md:col-span-1 border-t-4 border-t-blue-500 shadow-lg">
                        
                        <CardContent>
                          <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
                            <div className="rounded-lg border bg-card p-3">
                              <h3 className="font-medium flex items-center">
                                <FileText className="h-4 w-4 mr-2 text-primary" /> Product Backlog
                              </h3>
                              <div className="mt-2 space-y-1">
                                <div className="text-sm flex justify-between items-center">
                                  <span>Total Items</span>
                                  <Badge variant="outline">{dummyBacklog.length}</Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>High Priority</span>
                                  <Badge className="bg-orange-500">{dummyBacklog.filter(task => task.priority === 3).length}</Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Medium Priority</span>
                                  <Badge className="bg-orange-500">{dummyBacklog.filter(task => task.priority === 2).length}</Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Low Priority</span>
                                  <Badge className="bg-orange-500">{dummyBacklog.filter(task => task.priority === 1).length}</Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Total Points</span>
                                  <Badge variant="outline">{dummyBacklog.reduce((sum, task) => sum + task.story_points, 0)}</Badge>
                                </div>
                              </div>
                            </div>
                            
                            <div className="rounded-lg border bg-card p-3">
                              <h3 className="font-medium flex items-center">
                                <History className="h-4 w-4 mr-2 text-accent" /> Sprint History
                              </h3>
                              <div className="mt-2 space-y-1">
                              <div className="text-sm flex justify-between items-center">
                                  <span>Previous Sprint</span>
                                  <Badge className="bg-accent">
                                    {previousSprintName}
                                  </Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Completed Sprints</span>
                                  <Badge variant="outline">{sprintHistoryList.length}</Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Avg. Velocity</span>
                                  <Badge className="bg-accent">
                                    {Math.round(sprintHistoryList.reduce((sum, sprint) => sum + sprint.lagged_velocity, 0) / sprintHistoryList.length)}
                                  </Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Completion Rate</span>
                                  <Badge variant="outline" className="bg-green-500/10 text-green-700">
                                    {Math.round(sprintHistoryList.reduce((sum, s) => sum + s.completed_story_points, 0) / sprintHistoryList.reduce((sum, s) => sum + s.committed_story_points, 0) * 100)}%
                                  </Badge>
                                </div>
                                
                              </div>
                            </div>
                            
                            <div className="rounded-lg border bg-card p-3">
                              <h3 className="font-medium flex items-center">
                                <Users className="h-4 w-4 mr-2 text-secondary" /> Team Data
                              </h3>
                              <div className="mt-2 space-y-1">
                                <div className="text-sm flex justify-between items-center">
                                  <span>Team Members</span>
                                  <Badge variant="outline">{teamData.length}</Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Total Capacity</span>
                                  <Badge className="bg-secondary">{teamData.reduce((sum, member) => sum + member.capacity, 0)}</Badge>
                                </div>
                                <div className="text-sm flex justify-between items-center">
                                  <span>Avg. Capacity</span>
                                  <Badge variant="outline">
                                    {Math.round(teamData.reduce((sum, member) => sum + member.capacity, 0) / teamData.length)}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      
                    </div>
                  </TabsContent>

                  <TabsContent value="backlog">
                    <Card className="border-t-4 border-t-accent shadow-lg">
                      <CardHeader className="bg-gradient-to-r from-accent/10 to-transparent flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                        <CardTitle className="flex items-center">
                          <FileText className="mr-2 text-accent" /> Product Backlog
                        </CardTitle>
                        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                          <div className="relative flex-1 sm:w-64">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input placeholder="Search backlog..." className="pl-8" value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
                          </div>
                          <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm" className="text-xs h-9">
                              <Filter className="h-4 w-4 mr-1" /> Filter
                            </Button>
                            <Button variant="outline" size="sm" className="text-xs h-9">
                              <Download className="h-4 w-4 mr-1" /> Export
                            </Button>
                            <Button variant="default" size="sm" className="text-xs h-9" onClick={handleSyncFromJIRA}>
                              Sync from JIRA
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="rounded-lg border">
                          <Table>
                            <TableCaption>Available items in product backlog • {filteredBacklog.length} items • {filteredBacklog.reduce((sum, task) => sum + task.points, 0)} total points</TableCaption>
                            <TableHeader>
                              <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>Summary</TableHead>
                                <TableHead>Priority</TableHead>
                                <TableHead>Points</TableHead>
                                <TableHead>Required Skills</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead></TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {filteredBacklog.map(task => <React.Fragment key={task.issue_key}>
                                  <TableRow className="hover:bg-muted/50 cursor-pointer" onClick={() => setExpandedTask(expandedTask === task.issue_key ? null : task.issue_key)}>
                                    <TableCell className="font-medium">{task.issue_key}</TableCell>
                                    <TableCell className="max-w-xs">
                                      <div className="truncate">{task.summary}</div>
                                    </TableCell>
                                    <TableCell>{getPriorityBadge(task.priority)}</TableCell>
                                    <TableCell>
                                      <Badge variant="outline" className="bg-secondary/10">
                                        {task.points} pts
                                      </Badge>
                                    </TableCell>
                                    <TableCell>
                                      <div className="flex flex-wrap gap-1">
                                        {task.skills.split(", ").map(skill => <Badge key={skill} variant="outline" className="text-xs bg-primary/10 text-primary">
                                            {skill}
                                          </Badge>)}
                                      </div>
                                    </TableCell>
                                    <TableCell>
                                      <Badge className={`
                                        ${task.status === "To Do" ? "bg-muted text-muted-foreground" : ""}
                                        ${task.status === "In Progress" ? "bg-blue-500" : ""}
                                        ${task.status === "Done" ? "bg-green-500" : ""}
                                      `}>
                                        {task.status}
                                      </Badge>
                                    </TableCell>
                                    <TableCell>
                                      <Button variant="ghost" size="icon" onClick={e => {
                                    e.stopPropagation();
                                    setExpandedTask(expandedTask === task.issue_key ? null : task.issue_key);
                                  }}>
                                        {expandedTask === task.issue_key ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
                                      </Button>
                                    </TableCell>
                                  </TableRow>
                                  {expandedTask === task.issue_key && <TableRow className="bg-muted/30 hover:bg-muted/50">
                                      <TableCell colSpan={7} className="p-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                          <div>
                                            <h4 className="font-medium mb-2">Description</h4>
                                            <p className="text-sm text-muted-foreground">{task.description}</p>
                                            
                                            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                                              <div>
                                                <span className="text-muted-foreground">Type:</span>
                                                <Badge className="ml-2 bg-purple-500/80">{task.type}</Badge>
                                              </div>
                                              <div>
                                                <span className="text-muted-foreground">Created:</span>
                                                <span className="ml-2">{task.created}</span>
                                              </div>
                                              <div>
                                                <span className="text-muted-foreground">Assigned:</span>
                                                <span className="ml-2">{task.assigned}</span>
                                              </div>
                                              <div>
                                                <span className="text-muted-foreground">Status:</span>
                                                <Badge className={`ml-2
                                                  ${task.status === "To Do" ? "bg-muted text-muted-foreground" : ""}
                                                  ${task.status === "In Progress" ? "bg-blue-500" : ""}
                                                  ${task.status === "Done" ? "bg-green-500" : ""}
                                                `}>
                                                  {task.status}
                                                </Badge>
                                              </div>
                                            </div>
                                          </div>
                                          
                                          <div className="bg-card p-3 rounded-lg border">
                                            <h4 className="font-medium mb-2 flex items-center">
                                              <TrendingUp className="h-4 w-4 mr-2 text-primary" /> AI Analysis
                                            </h4>
                                            <div className="space-y-3 text-sm">
                                              <div>
                                                <span className="text-muted-foreground">Estimated Completion:</span>
                                                <span className="ml-2 font-medium">{task.points / 3} days</span>
                                              </div>
                                              <div>
                                                <span className="text-muted-foreground">Best Team Member Match:</span>
                                                <Badge className="ml-2 bg-accent">{task.assigned}</Badge>
                                              </div>
                                              <div>
                                                <span className="text-muted-foreground">Confidence:</span>
                                                <div className="w-full bg-muted rounded-full h-2 mt-1">
                                                  <div className="bg-gradient-to-r from-primary to-accent h-2 rounded-full" style={{
                                              width: `${85 - Number(task.issue_key.slice(-1)) * 5}%`
                                            }}></div>
                                                </div>
                                              </div>
                                              <div>
                                                <span className="text-muted-foreground">Dependencies:</span>
                                                <div className="flex gap-1 mt-1">
                                                  {task.issue_key !== "TSK-001" && <Badge variant="outline" className="text-xs">TSK-00{Number(task.issue_key.split("-")[1]) - 1}</Badge>}
                                                </div>
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      </TableCell>
                                    </TableRow>}
                                </React.Fragment>)}
                            </TableBody>
                          </Table>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                          <Card className="border-t-4 border-t-primary">
                            <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent">
                              <CardTitle className="flex items-center">
                                <PieChartIcon className="mr-2 text-primary" /> Task Priority Distribution
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="h-[300px] flex items-center justify-center">
                              <PieChart {...extendedChartConfig.priority} />
                            </CardContent>
                          </Card>
                          
                          <Card className="border-t-4 border-t-accent">
                            <CardHeader className="bg-gradient-to-r from-accent/10 to-transparent">
                              <CardTitle className="flex items-center">
                                <BarChartIcon className="mr-2 text-accent" /> Story Points by Type
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="h-[300px]">
                              <BarChart {...extendedChartConfig.points} />
                            </CardContent>
                          </Card>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="history">
                    <Card className="border-t-4 border-t-accent shadow-lg">
                      <CardHeader className="bg-gradient-to-r from-accent/10 to-transparent flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                        <CardTitle className="flex items-center">
                          <History className="mr-2 text-accent" /> Sprint History
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm" className="text-xs h-8">
                            <Download className="h-4 w-4 mr-1" /> Export
                          </Button>
                          <Button variant="outline" size="sm" className="text-xs h-8">
                            <Filter className="h-4 w-4 mr-1" /> Filter
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                          <Card className="bg-gradient-to-br from-primary/5 to-transparent border-primary/20">
                            <CardContent className="p-4">
                              <div className="flex justify-between items-center">
                                <p className="text-primary font-medium">Avg. Velocity</p>
                                <Badge className="bg-primary">{Math.round(sprintHistory.reduce((sum, s) => sum + s.velocity, 0) / sprintHistory.length)}</Badge>
                              </div>
                              <div className="mt-2">
                                <Progress value={80} className="h-1.5" />
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">
                                Story points delivered per sprint
                              </p>
                            </CardContent>
                          </Card>
                          <Card className="bg-gradient-to-br from-secondary/5 to-transparent border-secondary/20">
                            <CardContent className="p-4">
                              <div className="flex justify-between items-center">
                                <p className="text-secondary font-medium">On-time Delivery</p>
                                <Badge className="bg-secondary">83%</Badge>
</div>
                              <div className="mt-2">
                                <Progress value={83} className="h-1.5" />
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">
                                Percent of sprints meeting commitments
                              </p>
                            </CardContent>
                          </Card>
                          <Card className="bg-gradient-to-br from-accent/5 to-transparent border-accent/20">
                            <CardContent className="p-4">
                              <div className="flex justify-between items-center">
                                <p className="text-accent font-medium">Scope Change</p>
                                <Badge className="bg-accent">15%</Badge>
                              </div>
                              <div className="mt-2">
                                <Progress value={15} className="h-1.5" />
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">
                                Average scope change during sprints
                              </p>
                            </CardContent>
                          </Card>
                        </div>
                        
                        <div className="rounded-lg border mb-8">
                          <Table>
                            <TableCaption>Detailed sprint history • {sprintHistory.length} sprints</TableCaption>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Sprint</TableHead>
                                <TableHead>Duration</TableHead>
                                <TableHead>Planned Points</TableHead>
                                <TableHead>Completed</TableHead>
                                <TableHead>Team Members</TableHead>
                                <TableHead>Completion Rate</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {sprintHistory.map(sprint => <TableRow key={sprint.id} className="hover:bg-muted/50">
                                  <TableCell className="font-medium">{sprint.name}</TableCell>
                                  <TableCell>{sprint.endDate ? new Date(sprint.endDate).getDate() - new Date(sprint.startDate).getDate() : 14} days</TableCell>
                                  <TableCell>
                                    <Badge variant="outline">{sprint.plannedPoints} pts</Badge>
                                  </TableCell>
                                  <TableCell>
                                    <Badge variant="outline" className="bg-secondary/10">{sprint.completedPoints} pts</Badge>
                                  </TableCell>
                                  <TableCell>{teamData.filter(m => m.role !== "Product Owner").length}</TableCell>
                                  <TableCell>
                                    <div className="flex items-center gap-2">
                                      <Progress value={getCompletionRate(sprint.completedPoints, sprint.plannedPoints)} className="h-2 w-24" />
                                      <span className="text-xs font-medium">
                                        {getCompletionRate(sprint.completedPoints, sprint.plannedPoints)}%
                                      </span>
                                    </div>
                                  </TableCell>
                                </TableRow>)}
                            </TableBody>
                          </Table>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <Card className="border-t-4 border-t-primary">
                            <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent">
                              <CardTitle className="flex items-center">
                                <TrendingUp className="mr-2 text-primary" /> Velocity Trend
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="h-[300px]">
                              <BarChart {...chartConfig.velocity} />
                            </CardContent>
                          </Card>
                          
                          <Card className="border-t-4 border-t-accent">
                            <CardHeader className="bg-gradient-to-r from-accent/10 to-transparent">
                              <CardTitle className="flex items-center">
                                <LineChart className="mr-2 text-accent" /> Burndown Chart - Last Sprint
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="h-[300px]">
                              <BarChart {...chartConfig.burndown} />
                            </CardContent>
                          </Card>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                  
                  <TabsContent value="results">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                      
                      <div className="md:col-span-3 space-y-6">
                        <Card className="border-t-4 border-t-primary shadow-lg">
                          <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent">
                            <CardTitle className="flex items-center">
                              <Award className="mr-2 text-primary" /> {currentSprintName}: Task Assignment
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            

                            
                        <div> 
                        <TaskAssignmentTable 
                          developers={teamData} 
                          startDate={currentSprintStart} 
                          endDate={currentSprintEnd}
                          sprintAssignment={sprintAssignment} 
                        />
                        </div>
                            
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-6">
                              <Card className="bg-muted/30">
                                <CardContent className="p-3">
                                  <p className="text-xs text-muted-foreground">Total Story Points</p>
                                  <p className="text-lg font-medium">{totalStoryPoint}</p>
                                </CardContent>
                              </Card>
                              <Card className="bg-muted/30">
                                <CardContent className="p-3">
                                  <p className="text-xs text-muted-foreground">Total Tasks</p>
                                  <p className="text-lg font-medium">{totalTasks}</p>
                                </CardContent>
                              </Card>
                              <Card className="bg-muted/30">
                                <CardContent className="p-3">
                                  <p className="text-xs text-muted-foreground">Forecasted Velocity</p>
                                  <p className="text-lg font-medium text-green-500">{forecastedVelocity}</p>
                                </CardContent>
                              </Card>
                              <Card className="bg-muted/30">
                                <CardContent className="p-3">
                                  <p className="text-xs text-muted-foreground">Risk Level</p>
                                  <p className={`text-lg font-medium ${
                                    riskCategory === "Overcommitted / High Risk" ? "text-red-500" :
                                    riskCategory === "Ambitious / Stretch" ? "text-orange-500" :
                                    riskCategory === "Realistic / On Track" ? "text-green-500" :
                                    riskCategory === "Conservative / Under-planned" ? "text-orange-500" :
                                    riskCategory === "Significantly Under-planned" ? "text-red-500" : ""
                                  }`}>{riskCategory}</p>
                                </CardContent>
                              </Card>
                              
                            </div>

                            <div className="mt-6 flex flex-col sm:flex-row justify-end gap-3">
                              <Button variant="outline">
                                <Download className="mr-2 h-4 w-4" /> Export Plan
                              </Button>
                              <Button onClick={handleApprovePlan}>
                                <Check className="mr-2 h-4 w-4" /> Approve Plan
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                        
                        

                        <SprintChatbot 
  sprintName={getCurrentSprint().name} 
  sprintData={getCurrentSprint()} 
  setSprintAssignment={setSprintAssignment} 
  setTotalStoryPoint={setTotalStoryPoint}
  setTotalTasks={setTotalTasks}
  setRiskCategory={setRiskCategory}
  forecastedVelocity={forecastedVelocity}
/>
                        
                        
                      </div>
                      
                      <div className="space-y-6">
                        
                        
                        

                        
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="insights">
                    <InsightsTab />
                  </TabsContent>
                </Tabs>
              </>
            )}
          
        
      })()}

      {isLoading && (
  <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
    <div className="text-center">
      <div className="loader border-t-4 border-b-4 border-primary rounded-full w-12 h-12 animate-spin"></div>
      <p className="mt-4 text-white"></p>
    </div>
  </div>
)}

          </main>
        </div>
      </div>
    </div>
  );
};

const InsightsTab = () => {
  const [insightsData, setInsightsData] = useState<string>("Loading insights...");

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await axios.post("http://localhost:8000/api/chatSummary", {
          message: "hi",
        });

        // Format the response data for better readability
        const formattedData = formatInsights(response.data);
        setInsightsData(formattedData);
      } catch (error) {
        console.error("Error fetching insights:", error);
        setInsightsData("Failed to load insights. Please try again later.");
      }
    };

    fetchInsights();
  }, []);

  const formatInsights = (data: any): string => {
    // Assuming the response contains a summary field
    if (data && data.response) {
      // Remove unwanted characters and format the response
      const cleanedResponse = data.response
        .replace(/[#*]/g, "") // Remove # and * characters
       // .replace(/\n{2,}/g, "\n") // Replace multiple newlines with a single newline
        .trim();

      return `${cleanedResponse}`;
    }
    return "No insights available.";
  };

  return (
    <Card className="border-t-4 border-t-primary shadow-lg">
      <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent">
        <CardTitle className="flex items-center">
          <TrendingUp className="mr-2 text-primary" /> Sprint Insights
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="p-4 bg-muted/10 rounded-lg border border-muted/20">
          <textarea
            className="w-full h-96 p-4 text-base font-sans bg-white border border-muted rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
            readOnly
            value={insightsData}
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default SprintPlanningDashboard;

