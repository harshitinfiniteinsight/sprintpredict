import React, { useState,useEffect,useMemo } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Table, TableCaption, TableHeader, TableRow, TableHead, TableBody, TableCell } from "../components/ui/table";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Search, Filter, Download, ArrowUp, ArrowDown, FileText,TrendingUp } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import axios from "axios";

const ProductBacklog = ({ dummyBacklog1}) => {
  const [dummylog, setDummyBacklog] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedTask, setExpandedTask] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "3":
        return <Badge className="bg-red-500">High</Badge>;
      case "2":
        return <Badge>Medium</Badge>; // Default color
      case "1":
        return <Badge className="bg-gray-500">Low</Badge>; // Changed to Grey
      default:
        return <Badge>{priority}</Badge>;
    }
  };

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

  const filteredBacklog = useMemo(() => {
    return dummylog.filter(task =>
      task.issue_key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.assigned.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.skills.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [dummylog, searchTerm]);

  const handleSyncFromJIRA = async () => {
    try {
      const response1 = await axios.get("http://localhost:8000/api/sync/jira");
      const response = await axios.get("http://localhost:8000/api/backlog/tasks");
      setDummyBacklog(response.data.tasks);
      console.log("Fetched tasks from JIRA:", response.data.tasks);
      
      
      setRefreshKey(prevKey => prevKey + 1); 
      console.log("Filtered tasks:", filteredBacklog);
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
    <Card key={refreshKey} className="border-t-4 border-accent shadow-lg">
                      <CardHeader className="bg-gradient-to-r from-accent/10 to-transparent flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                        <CardTitle className="flex items-center">
                          <FileText className="mr-2 text-accent" /> Product Backlog
                        </CardTitle>
                        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                          
                          <div className="flex items-center gap-2">
                            
                            <Button variant="default" size="sm" className="text-xs h-9" onClick={handleSyncFromJIRA}>
                              Sync from JIRA
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="rounded-lg border">
                          <Table>
                            <TableCaption>Available items in product backlog • {filteredBacklog.length} items • {filteredBacklog.reduce((sum, task) => sum + task.story_points, 0)} total points</TableCaption>
                            <TableHeader>
                              <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>Summary</TableHead>
                                <TableHead>Priority</TableHead>
                                <TableHead>Points</TableHead>
                                <TableHead>Required Skills</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Dependency</TableHead>
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
                                    <TableCell>{getPriorityBadge(task.priority.toString())}</TableCell>
                                    <TableCell>
                                      <Badge variant="outline" className="bg-secondary/10">
                                        {task.story_points} pts
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
                                      <div className="flex flex-wrap gap-1">
                                        {task.dependencies.split(", ").map(dep => <Badge key={dep} variant="outline" className="text-xs bg-primary/10 text-primary">
                                            {dep}
                                          </Badge>)}
                                      </div>
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
                                        <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
                                          <div>
                                            <h4 className="font-medium mb-2">Summary</h4>
                                            <p className="text-sm text-muted-foreground">{task.summary}</p>
                                            
                                            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                                              <div>
                                                <span className="font-medium mb-2">Description:</span>
                                                <p className="text-sm text-muted-foreground">{task.description}</p>
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

                       
                      </CardContent>
                    </Card>
  );
};

export default ProductBacklog;