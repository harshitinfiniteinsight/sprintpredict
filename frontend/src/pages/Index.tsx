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
import { Upload, FileText, Users, Activity, Gift, Calendar as CalendarIcon, CheckCircle2, Clock, AlertTriangle, Award, TrendingUp, ChevronRight, History, Filter, LineChart, BarChart as BarChartIcon, PieChart as PieChartIcon, Download, Search, ArrowUp, ArrowDown, Link, List, Layers, Maximize, Check } from "lucide-react";
import { teamData1, sprintHistory,dummyBacklog1, sprintSummary, chartConfig, velocityData, burndownData } from "@/data/dummyData";
import BarChart from "@/components/ui/charts/BarChart";
import PieChart from "@/components/ui/charts/PieChart";
import SprintChatbot from "@/components/SprintChatbot";
import { format, addDays, isWeekend } from "date-fns";


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

const TaskAssignmentTable = ({ developers, startDate, endDate,sprintAssignment }) => {
  const workingDays = getWorkingDays(startDate, endDate);

  // Updated dummy task assignments for demonstration
  /*const dummyAssignments = {
    "Developer 1": {
      "2025-04-07": ["Task 1", "Task 2"],
      "2025-04-08": ["Task 1", "Task 3"],
    },
    "Developer 2": {
      "2025-04-07": ["Task 4"],
      "2025-04-08": ["Task 5", "Task 6"],
    },
    "Developer 3": {
      "2025-04-07": ["Task 7"],
      "2025-04-09": ["Task 8", "Task 9"],
    },
  };*/

  const dummyAssignments = React.useMemo(() => {
    const assignments = {};
    console.log("Sprint Assignment:", sprintAssignment);
    Object.entries(sprintAssignment || {}).forEach(([developer, data]) => {
      if (data.schedule) {
        Object.entries(data.schedule).forEach(([date, tasks]) => {
          tasks.forEach((taskEntry) => {
            if (!assignments[developer]) {
              assignments[developer] = {};
            }
            if (!assignments[developer][date]) {
              assignments[developer][date] = [];
            }
            assignments[developer][date].push({
              task: taskEntry.task,
              points: taskEntry.points
            });
          });
        });
      }
    });
    return assignments;
  }, [sprintAssignment]);

  console.log("Dummy Assignments:", dummyAssignments);

  const renderTaskBlocks = (developerName, day, task) => {
    const isContinuation = workingDays.some((prevDay) => {
      const prevDate = format(prevDay, "yyyy-MM-dd");
      return dummyAssignments[developerName]?.[prevDate]?.some(t => t.task === task.task);
    });

    const truncatedTask = task.task.length > 15 ? `${task.task.slice(0, 15)}...` : task.task;

    return (
      <div
        className={`${getTaskColor(task.task)} text-black p-1 rounded text-center whitespace-nowrap ${isContinuation ? "rounded-l-none" : ""}`}
        title={`Task: ${task.task}\nPoints: ${task.points}\nDeveloper: ${developerName}`}
      >
        <div>{truncatedTask}</div>
        <div className="text-xs">{task.points} pts</div>
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

const SprintPlanningDashboard = () => {
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
    const fetchBacklog = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/team/members");
        console.log("Backlog data fetched:", response.data);
        setTeamData(response.data.members);
      } catch (error) {
        console.error("Error fetching backlog data:", error);
      }
    };

    fetchBacklog();
  }, []);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    toast({
      title: "Section Changed",
      description: `Moved to ${value} section`
    });
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
  const [isLoading, setIsLoading] = useState(false);
  const generatePlan = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/sprint/task-distribution");
      console.log("Sprint assignment data:",response.data.optimization_summary.developer_utilization);
      setSprintAssignment(response.data.optimization_summary.developer_utilization);
      
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setActiveTab("results");
        toast({
          title: "Sprint Plan Generated",
          description: "AI has generated the optimal sprint plan based on the provided data."
        });
      }, 4000);
    } catch (error) {
      console.error("Error syncing from JIRA:", error);
      toast({
        title: "Sync Failed",
        description: "Could not refresh Product Backlog from JIRA.",
        variant: "destructive"
      });
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary/30 via-background to-background">
      {isLoading && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="flex flex-col items-center">
            <svg
              className="animate-spin h-8 w-8 text-white mb-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 2.42.879 4.63 2.343 6.343l1.657-1.052z"
              ></path>
            </svg>
            <div className="text-white text-lg font-bold">Generating Sprint Plan...</div>
          </div>
        </div>
      )}
      <header className="bg-gradient-to-r from-primary to-accent p-6 text-white relative overflow-hidden">
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
          <p className="text-white/80 max-w-xl">AI-Driven Sprint Planning & Prioritization System that optimizes team workload and maximizes delivery efficiency</p>
          
          {/* <div className="flex flex-wrap gap-3 mt-4">
            <Badge className="bg-white/20 hover:bg-white/30 transition-colors">AI-Powered</Badge>
            <Badge className="bg-white/20 hover:bg-white/30 transition-colors">Machine Learning</Badge>
            <Badge className="bg-white/20 hover:bg-white/30 transition-colors">Team Optimization</Badge>
            <Badge className="bg-white/20 hover:bg-white/30 transition-colors">Resource Planning</Badge>
          </div> */}
        </div>
      </header>

      <main className="container mx-auto py-8 px-4">
        <div className="mb-8 flex flex-col md:flex-row items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold gradient-text">Sprint Planning Dashboard</h2>
            <p className="text-muted-foreground">Plan, prioritize, and predict your sprint outcomes</p>
          </div>
          
          <div className="flex items-center mt-4 md:mt-0 space-x-2 bg-card p-3 rounded-lg shadow-lg border border-primary/20">
            <CalendarIcon className="text-primary" size={20} />
            <span>Today: {new Date().toLocaleDateString()}</span>
            <Badge className="ml-2 bg-gradient-to-r from-accent to-primary">{getCurrentSprint().name}</Badge>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <Label>Current Sprint:</Label>
            <div className="flex flex-wrap gap-2">
              {sprints.map(sprint => <Button key={sprint.id} variant={currentSprintId === sprint.id ? "default" : "outline"} onClick={() => setCurrentSprintId(sprint.id)} className="h-8">
                  {sprint.name}
                </Button>)}
              <Button variant="outline" className="border-dashed h-8" onClick={createNewSprint}>
                + New Sprint
              </Button>
            </div>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
          <TabsList className="grid grid-cols-5 mb-8 bg-card p-1 rounded-xl shadow-md">
            <TabsTrigger value="upload" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
              <Upload size={18} /> Sprint Details
            </TabsTrigger>
            <TabsTrigger value="team" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
              <Users size={18} /> Team Data
            </TabsTrigger>
            <TabsTrigger value="backlog" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
              <FileText size={18} /> Product Backlog
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
              <History size={18} /> Sprint History
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
              <Activity size={18} /> Results
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              

              <Card className="md:col-span-2 border-t-4 border-t-secondary shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="bg-gradient-to-r from-secondary/10 to-transparent">
                  <CardTitle className="flex items-center">
                    <TrendingUp className="mr-2 text-secondary" /> Sprint Configuration
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
                  <div className="space-y-2">
                    <Label htmlFor="sprint-name" className="flex items-center">
                      <Award className="h-4 w-4 mr-2 text-secondary" /> Sprint Name
                    </Label>
                    <Input id="sprint-name" defaultValue="Sprint 7" className="border-secondary/20 focus:border-secondary" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sprint-goal" className="flex items-center">
                      <CheckCircle2 className="h-4 w-4 mr-2 text-primary" /> Sprint Goal
                    </Label>
                    <Input id="sprint-goal" defaultValue="Complete user authentication and profile features" className="border-primary/20 focus:border-primary" />
                  </div>
                  <div className="space-y-2">
                    <Label className="flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-2 text-accent" /> Sprint Start Date
                    </Label>
                    <div className="border rounded-md p-2 bg-card">
                      <Calendar mode="single" selected={date} onSelect={setDate} className="rounded-md" />
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="sprint-duration" className="flex items-center">
                        <Clock className="h-4 w-4 mr-2 text-accent" /> Sprint Duration (days)
                      </Label>
                      <Input id="sprint-duration" type="number" defaultValue="14" className="border-accent/20 focus:border-accent" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="planning-threshold" className="flex items-center">
                        <AlertTriangle className="h-4 w-4 mr-2 text-orange-500" /> Planning Threshold (%)
                      </Label>
                      <Input id="planning-threshold" type="number" defaultValue="70" className="border-orange-500/20 focus:border-orange-500" />
                      <div className="w-full bg-muted rounded-full h-2 mt-2">
                        <div className="bg-gradient-to-r from-primary to-accent h-2 rounded-full" style={{
                        width: '70%'
                      }}></div>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        Recommended threshold: 65-75% of team capacity to allow for unforeseen tasks
                      </p>
                    </div>
                    <Button className="mt-4 w-full bg-gradient-to-r from-primary to-accent hover:opacity-90 pulse-primary" onClick={generatePlan}>
                      Generate Sprint Plan <ChevronRight className="ml-1" size={16} />
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="md:col-span-2 border-t-4 border-t-blue-500 shadow-lg">
                <CardHeader className="bg-gradient-to-r from-blue-500/10 to-transparent">
                  <CardTitle className="flex items-center">
                    <LineChart className="mr-2 text-blue-500" /> Data Preview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                          <Badge className="bg-orange-500">{dummyBacklog.filter(task => task.priority === 1).length}</Badge>
                        </div>
                        <div className="text-sm flex justify-between items-center">
                          <span>Total Points</span>
                          <Badge variant="outline">{dummyBacklog.reduce((sum, task) => sum + task.points, 0)}</Badge>
                        </div>
                      </div>
                    </div>
                    
                    <div className="rounded-lg border bg-card p-3">
                      <h3 className="font-medium flex items-center">
                        <History className="h-4 w-4 mr-2 text-accent" /> Sprint History
                      </h3>
                      <div className="mt-2 space-y-1">
                        <div className="text-sm flex justify-between items-center">
                          <span>Completed Sprints</span>
                          <Badge variant="outline">{sprintHistory.length}</Badge>
                        </div>
                        <div className="text-sm flex justify-between items-center">
                          <span>Avg. Velocity</span>
                          <Badge className="bg-accent">
                            {Math.round(sprintHistory.reduce((sum, sprint) => sum + sprint.velocity, 0) / sprintHistory.length)}
                          </Badge>
                        </div>
                        <div className="text-sm flex justify-between items-center">
                          <span>Completion Rate</span>
                          <Badge variant="outline" className="bg-green-500/10 text-green-700">
                            {Math.round(sprintHistory.reduce((sum, s) => sum + s.completedPoints, 0) / sprintHistory.reduce((sum, s) => sum + s.plannedPoints, 0) * 100)}%
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

          <TabsContent value="team">
            <Card className="border-t-4 border-primary shadow-lg">
              <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <CardTitle className="flex items-center">
                  <Users className="mr-2 text-primary" /> Team Data
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
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-6">
                  {teamData.map(member => <Card key={member.name} className="shadow-md hover:shadow-lg transition-shadow border-l-4 border-l-accent relative overflow-hidden group">
                      <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-primary/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                      <CardHeader className="p-4 pb-2">
                        <CardTitle className="text-lg flex justify-between items-center">
                          <span>{member.name}</span>
                          <Badge variant="outline" className="text-xs">{member.capacity} pts</Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-4 pt-0">
                        <p className="text-sm text-muted-foreground">{member.role}</p>
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Capacity</span>
                            <span className="font-medium">{member.capacity} pts</span>
                          </div>
                          <Progress value={member.capacity / 20 * 100} className="h-2 mt-1" />
                        </div>
                        <div className="mt-3">
                          <p className="text-xs text-muted-foreground mb-1">Skills:</p>
                          <div className="flex flex-wrap gap-1">
                            {member.skills.split(", ").map(skill => <Badge key={skill} variant="outline" className="text-xs bg-accent/10 text-accent-foreground">
                                {skill}
                              </Badge>)}
                          </div>
                        </div>
                        <div className="mt-3 text-xs text-muted-foreground">
                          <a href={`mailto:${member.email}`} className="hover:text-primary">{member.email}</a>
                        </div>
                      </CardContent>
                    </Card>)}
                </div>

                <div className="rounded-lg border">
                  <Table>
                    <TableCaption>Sprint planning team data</TableCaption>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead>Capacity (Points)</TableHead>
                        <TableHead>Skills</TableHead>
                        <TableHead>Email</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {teamData.map(member => <TableRow key={member.name} className="hover:bg-muted/50">
                          <TableCell className="font-medium">{member.name}</TableCell>
                          <TableCell>{member.role}</TableCell>
                          <TableCell>
                            <Badge variant="outline" className="bg-secondary/10">
                              {member.capacity} pts
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-wrap gap-1">
                              {member.skills.split(", ").slice(0, 2).map(skill => <Badge key={skill} variant="outline" className="text-xs bg-primary/10 text-primary">
                                  {skill}
                                </Badge>)}
                              {member.skills.split(", ").length > 2 && <Badge variant="outline" className="text-xs">
                                  +{member.skills.split(", ").length - 2}
                                </Badge>}
                            </div>
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {member.email}
                          </TableCell>
                        </TableRow>)}
                    </TableBody>
                  </Table>
                </div>
                
                <Card className="mt-8 border-t-4 border-t-secondary">
                  <CardHeader className="bg-gradient-to-r from-secondary/10 to-transparent">
                    <CardTitle className="flex items-center">
                      <BarChartIcon className="mr-2 text-secondary" /> Team Capacity Visualization
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="h-[600px]">
                    <BarChart {...chartConfig.capacity} />
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="backlog">
            <Card className="border-t-4 border-accent shadow-lg">
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
              <div className="md:col-span-1 space-y-6">
              </div>
              <div className="md:col-span-3 space-y-6">
                <Card className="border-t-4 border-t-primary shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent">
                    <CardTitle className="flex items-center">
                      <Award className="mr-2 text-primary" /> Recommended Sprint Plan
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4 p-3 bg-gradient-to-br from-primary/5 to-secondary/5 rounded-lg border border-primary/10">
                      <h3 className="text-lg font-medium mb-1">{getCurrentSprint().name}: {getCurrentSprint().goal}</h3>
                      <p className="text-sm text-muted-foreground">
                        {getCurrentSprint().startDate} - {getCurrentSprint().endDate} • {getCurrentSprint().duration} days • {getCurrentSprint().totalPoints} story points • {getCurrentSprint().teamMembers} team members
                      </p>
                    </div>

                    <Card className="border-t-4 border-t-primary shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent">
                    <CardTitle className="flex items-center">
                      Task Assignment
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <TaskAssignmentTable 
                      developers={teamData} 
                      startDate={getCurrentSprint().startDate} 
                      endDate={getCurrentSprint().endDate}
                      sprintAssignment={sprintAssignment} 
                    />
                  </CardContent>
                </Card>
                    
                    
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-6">
                      <Card className="bg-muted/30">
                        <CardContent className="p-3">
                          <p className="text-xs text-muted-foreground">Total Story Points</p>
                          <p className="text-lg font-medium">{dummyBacklog.slice(0, 7).reduce((sum, task) => sum + task.points, 0)}</p>
                        </CardContent>
                      </Card>
                      <Card className="bg-muted/30">
                        <CardContent className="p-3">
                          <p className="text-xs text-muted-foreground">Total Tasks</p>
                          <p className="text-lg font-medium">{dummyBacklog.slice(0, 7).length}</p>
                        </CardContent>
                      </Card>
                      <Card className="bg-muted/30">
                        <CardContent className="p-3">
                          <p className="text-xs text-muted-foreground">Risk Level</p>
                          <p className="text-lg font-medium text-amber-500">Medium</p>
                        </CardContent>
                      </Card>
                      <Card className="bg-muted/30">
                        <CardContent className="p-3">
                          <p className="text-xs text-muted-foreground">Team Utilization</p>
                          <p className="text-lg font-medium text-green-500">86%</p>
                        </CardContent>
                      </Card>
                    </div>

                    <div className="mt-6 flex flex-col sm:flex-row justify-end gap-3">
                      <Button variant="outline">
                        <Download className="mr-2 h-4 w-4" /> Export Plan
                      </Button>
                      <Button>
                        <Check className="mr-2 h-4 w-4" /> Approve Plan
                      </Button>
                    </div>
                  </CardContent>
                </Card>
                
                

                <SprintChatbot sprintName={getCurrentSprint().name} sprintData={getCurrentSprint()} />
                
                
              </div>
              
              <div className="space-y-6">
                <Card className="border-t-4 border-t-accent shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-accent/10 to-transparent">
                    <CardTitle className="flex items-center">
                      <Users className="mr-2 text-accent" /> Team Allocation
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {teamData.slice(0, 5).map(member => <div key={member.name} className="flex flex-col space-y-1">
                        <div className="flex justify-between items-center">
                          <p className="font-medium">{member.name.split(" ")[0]}</p>
                          <Badge variant="outline" className={member.capacity > 16 ? "bg-red-500/20 text-red-600" : member.capacity > 12 ? "bg-amber-500/20 text-amber-600" : "bg-green-500/20 text-green-600"}>{member.capacity} pts</Badge>
                        </div>
                        <Progress value={member.capacity / 20 * 100} className={`h-2 ${member.capacity > 16 ? "bg-red-500" : member.capacity > 12 ? "bg-amber-500" : "bg-green-500"}`} />
                      </div>)}
                    <div className="h-[200px] mt-6">
                      <PieChart {...extendedChartConfig.allocation} />
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-t-4 border-t-green-500 shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-green-500/10 to-transparent">
                    <CardTitle className="flex items-center">
                      <CheckCircle2 className="mr-2 text-green-500" /> Sprint Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-3 rounded-lg bg-primary/10 border border-primary/30">
                      <h4 className="font-medium flex items-center text-primary">
                        <TrendingUp className="h-4 w-4 mr-2" /> Velocity
                      </h4>
                      <p className="text-xs text-muted-foreground mt-1">
                        Expected sprint velocity is 85 points, which is 15% higher than the team's average.
                      </p>
                    </div>
                    
                    <div className="p-3 rounded-lg bg-secondary/10 border border-secondary/30">
                      <h4 className="font-medium flex items-center text-secondary">
                        <CheckCircle2 className="h-4 w-4 mr-2" /> Completion Target
                      </h4>
                      <p className="text-xs text-muted-foreground mt-1">
                        Based on historical data, the team has an 87% chance of completing all committed tasks.
                      </p>
                    </div>
                    
                    <div className="p-3 rounded-lg bg-accent/10 border border-accent/30">
                      <h4 className="font-medium flex items-center text-accent">
                        <Users className="h-4 w-4 mr-2" /> Team Balance
                      </h4>
                      <p className="text-xs text-muted-foreground mt-1">
                        Workload is well-distributed among team members with skill-based task allocation.
                      </p>
                    </div>
                    
                    <div className="mt-4">
                      <p className="text-sm font-medium mb-2">Sprint Health</p>
                      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                        <div className="bg-gradient-to-r from-green-500 to-primary h-full" style={{
                        width: '85%'
                      }}></div>
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>Sprint Start</span>
                        <span>In Progress</span>
                        <span>Completion</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-t-4 border-t-blue-500 shadow-lg">
                  <CardHeader className="bg-gradient-to-r from-blue-500/10 to-transparent">
                    <CardTitle className="flex items-center">
                      <TrendingUp className="mr-2 text-blue-500" /> Previous Sprints Optimization
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm text-muted-foreground">
                      AI-powered insights from previous sprints to optimize current planning
                    </p>
                    
                    <div className="space-y-2">
                      {sprintHistory.slice(0, 3).map((sprint, index) => <div key={index} className="p-2 rounded-lg border bg-card">
                          <div className="flex justify-between items-center">
                            <span className="font-medium">{sprint.name}</span>
                            <Badge variant="outline">{sprint.completedPoints}/{sprint.plannedPoints} pts</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            Optimization: {index === 0 ? "Reduce frontend tasks by 10%" : index === 1 ? "Increase testing allocation" : "Balance backend workload"}
                          </p>
                        </div>)}
                    </div>
                    
                    <Button variant="outline" size="sm" className="w-full mt-2">
                      View All Optimizations
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};
export default SprintPlanningDashboard;
