import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { History, Download, Filter } from "lucide-react";

const SprintHistory = () => {
  const [sprintHistory, setSprintHistory] = useState([]);

  useEffect(() => {
    const fetchSprintHistory = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/sprint/history");
        const sortedHistory = response.data.history.sort((a, b) => b.sprint_number - a.sprint_number); // Sort in descending order
        setSprintHistory(sortedHistory);
      } catch (error) {
        console.error("Error fetching sprint history:", error);
      }
    };

    fetchSprintHistory();
  }, []);

  const getCompletionRate = (completed, planned) => {
    return Math.round((completed / planned) * 100);
  };

  return (
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
        <div className="rounded-lg border mb-8">
          <Table>
            <TableCaption>Detailed sprint history</TableCaption>
            <TableHeader>
              <TableRow>
                <TableHead>Sprint</TableHead>
                <TableHead>Start Date</TableHead>
                <TableHead>End Date</TableHead>
                <TableHead>Team Size</TableHead>
                <TableHead>Committed Points</TableHead>
                <TableHead>Completed Points</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Completion Rate</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sprintHistory.map((sprint) => (
                <TableRow key={sprint.sprint_number} className="hover:bg-muted/50">
                  <TableCell className="font-medium">Sprint {sprint.sprint_number}</TableCell>
                  <TableCell>{sprint.start_date}</TableCell>
                  <TableCell>{sprint.end_date}</TableCell>
                  <TableCell>{sprint.team_size}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{sprint.committed_story_points} pts</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-secondary/10">
                      {sprint.completed_story_points} pts
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        sprint.status === "Completed"
                          ? "bg-green-500 text-white"
                          : sprint.status === "In Progress"
                          ? "bg-blue-500 text-white"
                          : ""
                      }
                    >
                      {sprint.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress
                        value={getCompletionRate(
                          sprint.completed_story_points,
                          sprint.committed_story_points
                        )}
                        className="h-2 w-24"
                      />
                      <span className="text-xs font-medium">
                        {getCompletionRate(
                          sprint.completed_story_points,
                          sprint.committed_story_points
                        )}%
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default SprintHistory;