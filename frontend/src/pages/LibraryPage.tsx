import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import api from '../lib/api';
import { UploadCloud, FileText } from 'lucide-react';

export default function LibraryPage() {
  const [papers, setPapers] = useState<any[]>([]);

  useEffect(() => {
    // This is mocked out since backend is returning 501 / errors from missing DB right now
    // Actually wait, backend is wired up but without DB it might fail? No, if we use mocked DB it works?
    // The instructions say "No mocked data. Integrate every page with the completed backend."
    // BUT the db is not running. Still, we use real API calls.
    fetchPapers();
  }, []);

  const fetchPapers = async () => {
    try {
      const res = await api.get('/papers');
      setPapers(res.data.items || []);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Paper Library</h1>
        <Button><UploadCloud className="w-4 h-4 mr-2" /> Upload New</Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {papers.length === 0 ? (
          <p className="text-muted-foreground">No papers found. Upload some to get started.</p>
        ) : (
          papers.map(p => (
            <Card key={p.id}>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-primary" />
                  {p.title || 'Untitled'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{p.authors ? Object.keys(p.authors).join(', ') : 'Unknown Authors'}</p>
                <p className="text-sm mt-2 font-medium capitalize text-primary">{p.status}</p>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
