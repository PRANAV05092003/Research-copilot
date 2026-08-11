import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '../components/ui';
import api from '../lib/api';
import { Network } from 'lucide-react';

export default function GapAnalysisPage() {
  const [topic, setTopic] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);

  const handleAnalyze = async () => {
    try {
      const res = await api.post('/research/review', { topic: `Gap Analysis on: ${topic}` });
      setJobId(res.data.job_id);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3 mb-6">
        <Network className="w-8 h-8 text-primary" />
        <h1 className="text-3xl font-bold">Gap Analysis</h1>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Identify Literature Gaps</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input 
            placeholder="Domain to analyze for missing literature or contradictions..." 
            value={topic} 
            onChange={(e) => setTopic(e.target.value)} 
          />
          <Button onClick={handleAnalyze} disabled={!topic}>Run Analysis</Button>
          
          {jobId && (
            <div className="p-4 bg-muted rounded-md mt-4 border">
              <p className="font-semibold text-sm">Gap Analysis Job Queued!</p>
              <p className="text-xs text-muted-foreground break-all mt-1">ID: {jobId}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
