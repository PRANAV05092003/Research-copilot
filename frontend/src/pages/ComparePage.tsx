import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '../components/ui';
import api from '../lib/api';
import { GitCompare } from 'lucide-react';

export default function ComparePage() {
  const [topic, setTopic] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);

  const handleCompare = async () => {
    // Note: The backend currently only exposes a generic /research/review endpoint.
    // For comparison, we might use a dedicated job type in the future. 
    // We will call the deep research endpoint as a placeholder or adapt it to a compare endpoint if it existed.
    try {
      const res = await api.post('/research/review', { topic: `Compare papers regarding: ${topic}` });
      setJobId(res.data.job_id);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3 mb-6">
        <GitCompare className="w-8 h-8 text-primary" />
        <h1 className="text-3xl font-bold">Paper Comparison</h1>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Generate Comparison Report</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input 
            placeholder="E.g. Transformer architectures vs Recurrent Neural Networks..." 
            value={topic} 
            onChange={(e) => setTopic(e.target.value)} 
          />
          <Button onClick={handleCompare} disabled={!topic}>Run Comparison</Button>
          
          {jobId && (
            <div className="p-4 bg-muted rounded-md mt-4 border">
              <p className="font-semibold text-sm">Comparison Job Queued!</p>
              <p className="text-xs text-muted-foreground break-all mt-1">ID: {jobId}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
