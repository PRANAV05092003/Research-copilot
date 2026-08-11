import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '../components/ui';
import api from '../lib/api';
import { Microscope } from 'lucide-react';

export default function ResearchPage() {
  const [topic, setTopic] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const generateReview = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      const { data } = await api.post('/research/review', { topic });
      setJobId(data.job_id);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-3 mb-6">
        <Microscope className="w-8 h-8 text-primary" />
        <h1 className="text-3xl font-bold">Literature Review Generator</h1>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Autonomous Deep Research</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input 
            value={topic} 
            onChange={(e) => setTopic(e.target.value)} 
            placeholder="Enter a research topic (e.g., 'Attention mechanisms in vision transformers')" 
            className="text-base py-6 rounded-xl"
          />
          <Button onClick={generateReview} disabled={!topic || loading} className="w-full sm:w-auto px-8">
            {loading ? 'Queuing Job...' : 'Generate Deep Review'}
          </Button>
          
          {jobId && (
             <div className="p-4 bg-muted rounded-md mt-4 border">
               <p className="font-semibold text-sm text-primary">Research Job Queued Successfully!</p>
               <p className="text-xs text-muted-foreground mt-1">
                 The LangGraph agents are now searching, reading, verifying, and writing your review.
               </p>
               <p className="text-xs text-muted-foreground font-mono mt-2">Job ID: {jobId}</p>
             </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
