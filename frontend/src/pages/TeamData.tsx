import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { CalendarIcon, Download, Filter, Users } from "lucide-react";
import LeaveCalendar from "../components/LeaveCalendar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const TeamData = ({ teamData }) => {
  return (
    <Card className="border-t-4 border-primary shadow-lg">
      <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <CardTitle className="flex items-center">
          <Users className="mr-2 text-primary" /> Team Details
        </CardTitle>
        <div className="flex items-center gap-2">
          
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="team-data" className="w-full">
          <TabsList className="grid grid-cols-2 mb-8 bg-card p-1 rounded-xl shadow-md">
            <TabsTrigger value="team-data" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
              Team Data
            </TabsTrigger>
            <TabsTrigger value="leave-calendar" className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-white rounded-lg">
              Leave and Public Holiday Calendar
            </TabsTrigger>
          </TabsList>
          <TabsContent value="team-data">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-6">
              {teamData.map(member => (
                <Card key={member.name} className="shadow-md hover:shadow-lg transition-shadow border-l-4 border-l-accent relative overflow-hidden group">
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
                        {member.skills.split(", ").map(skill => (
                          <Badge key={skill} variant="outline" className="text-xs bg-accent/10 text-accent-foreground">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="mt-3 text-xs text-muted-foreground">
                      <a href={`mailto:${member.email}`} className="hover:text-primary">{member.email}</a>
                    </div>
                  </CardContent>
                </Card>
              ))}
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
                  {teamData.map(member => (
                    <TableRow key={member.name} className="hover:bg-muted/50">
                      <TableCell className="font-medium">{member.name}</TableCell>
                      <TableCell>{member.role}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary/10">
                          {member.capacity} pts
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {member.skills.split(", ").slice(0, 2).map(skill => (
                            <Badge key={skill} variant="outline" className="text-xs bg-primary/10 text-primary">
                              {skill}
                            </Badge>
                          ))}
                          {member.skills.split(", ").length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{member.skills.split(", ").length - 2}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {member.email}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
          <TabsContent value="leave-calendar">
            <LeaveCalendar />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default TeamData;