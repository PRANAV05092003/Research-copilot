import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '../components/ui';
import api from '../lib/api';
import { Search, FileText } from 'lucide-react';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const { data } = await api.post('/search', { query, top_k: 10, mode: 'hybrid' });
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-3 mb-6">
        <Search className="w-8 h-8 text-primary" />
        <h1 className="text-3xl font-bold">Hybrid Search</h1>
      </div>
      
      <form onSubmit={handleSearch} className="flex space-x-4">
        <Input 
          value={query} 
          onChange={(e) => setQuery(e.target.value)} 
          placeholder="Ask a question or enter keywords (e.g. 'How does self-attention work?')" 
          className="flex-1 text-base p-6 rounded-xl shadow-sm"
        />
        <Button type="submit" className="px-8 h-auto rounded-xl" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </form>

      <div className="space-y-4 mt-8">
        {results.map((result, idx) => (
          <Card key={idx} className="hover:border-primary/50 transition-colors">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center text-primary">
                <FileText className="w-4 h-4 mr-2" />
                {result.paper_title || 'Unknown Paper'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed">{result.text}</p>
              <div className="flex items-center space-x-4 mt-4 text-xs font-medium text-muted-foreground bg-muted p-2 rounded-md inline-flex">
                <span>Score: {(result.score || 0).toFixed(4)}</span>
                <span>Page: {result.page_number || 'N/A'}</span>
              </div>
            </CardContent>
          </Card>
        ))}
        {results.length === 0 && !loading && (
          <div className="text-center p-12 border rounded-xl bg-muted/20 border-dashed">
            <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-20" />
            <p className="text-muted-foreground font-medium">No results to display. Run a search to see matches across your library.</p>
          </div>
        )}
      </div>
    </div>
  );
}
