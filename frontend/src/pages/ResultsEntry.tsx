import { useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import { Search, Save, AlertTriangle, CheckCircle, X, ClipboardList } from 'lucide-react';

interface ResultParam {
  name: string;
  value: string;
  unit: string;
  reference_range: string;
  is_abnormal: boolean;
}

export default function ResultsEntry() {
  const [samples, setSamples] = useState<any[]>([]);
  const [selectedSample, setSelectedSample] = useState<any>(null);
  const [selectedTest, setSelectedTest] = useState<any>(null);
  const [results, setResults] = useState<ResultParam[]>([]);
  const [technician, setTechnician] = useState('');
  const [saving, setSaving] = useState(false);
  const [searchQ, setSearchQ] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadPendingSamples(); }, []);

  const loadPendingSamples = async () => {
    try {
      const { data } = await api.get('/samples', { params: { status: 'processing', limit: 200 } });
      setSamples(data.data || []);
    } catch {
      toast.error('Failed to load samples');
    } finally {
      setLoading(false);
    }
  };

  const selectSample = (sample: any) => {
    setSelectedSample(sample);
    setSelectedTest(null);
    setResults([]);
  };

  const selectTest = (test: any) => {
    setSelectedTest(test);
    // Build results from test parameters
    const params = test.parameters || [];
    setResults(params.map((p: any) => ({
      name: p.name,
      value: '',
      unit: p.unit || '',
      reference_range: p.reference_range_male || p.reference_range || '',
      is_abnormal: false,
    })));
  };

  const updateResult = (index: number, value: string) => {
    setResults((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], value };
      // Auto check if value is out of reference range
      const ref = updated[index].reference_range;
      if (ref && value) {
        const numVal = parseFloat(value);
        const rangeMatch = ref.match(/^([\d.]+)\s*-\s*([\d.]+)$/);
        if (rangeMatch && !isNaN(numVal)) {
          const low = parseFloat(rangeMatch[1]);
          const high = parseFloat(rangeMatch[2]);
          updated[index].is_abnormal = numVal < low || numVal > high;
        }
      }
      return updated;
    });
  };

  const handleSave = async () => {
    if (!selectedSample || !selectedTest) return toast.error('Select a sample and test');
    if (!technician) return toast.error('Enter technician name');
    if (results.some((r) => !r.value)) return toast.error('Fill all result values');

    setSaving(true);
    try {
      await api.post('/reports', {
        sample_id: selectedSample.id,
        test_id: selectedTest.id,
        results: results.map((r) => ({
          parameter_name: r.name,
          value: r.value,
          unit: r.unit,
          reference_range: r.reference_range,
          is_abnormal: r.is_abnormal,
        })),
        technician_name: technician,
      });
      toast.success('Results saved and report created!');
      setSelectedSample(null);
      setSelectedTest(null);
      setResults([]);
      setTechnician('');
      loadPendingSamples();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error saving results');
    } finally {
      setSaving(false);
    }
  };

  const filteredSamples = samples.filter((s) => {
    const q = searchQ.toLowerCase();
    return (s.sample_id || '').toLowerCase().includes(q) ||
      (s.patient_name || '').toLowerCase().includes(q);
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Results Entry</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Sample List */}
        <div className="lg:col-span-1">
          <div className="card p-4">
            <h2 className="font-semibold text-gray-900 mb-3">Pending Samples</h2>
            <div className="relative mb-3">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
              <input
                className="input-field pl-9 text-sm"
                placeholder="Search sample or patient..."
                value={searchQ}
                onChange={(e) => setSearchQ(e.target.value)}
              />
            </div>
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin h-6 w-6 border-4 border-accent-500 border-t-transparent rounded-full" />
              </div>
            ) : filteredSamples.length > 0 ? (
              <div className="space-y-1 max-h-[60vh] overflow-y-auto">
                {filteredSamples.map((s) => (
                  <button key={s.id}
                    onClick={() => selectSample(s)}
                    className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition ${
                      selectedSample?.id === s.id
                        ? 'bg-primary-50 border border-primary-200'
                        : 'hover:bg-gray-50 border border-transparent'
                    }`}>
                    <div className="font-medium text-primary-600">{s.sample_id}</div>
                    <div className="text-gray-500 text-xs mt-0.5">{s.patient_name}</div>
                    <div className="text-gray-400 text-xs">
                      {(s.tests || []).map((t: any) => t.name).join(', ')}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-gray-400 text-sm">
                <ClipboardList className="w-10 h-10 mx-auto mb-2 opacity-40" />
                No pending samples
              </div>
            )}
          </div>
        </div>

        {/* Results Entry Area */}
        <div className="lg:col-span-2">
          {selectedSample ? (
            <div className="card p-5">
              {/* Sample Info */}
              <div className="flex items-center justify-between mb-4 pb-3 border-b">
                <div>
                  <h2 className="font-bold text-lg text-primary-600">{selectedSample.sample_id}</h2>
                  <p className="text-sm text-gray-500">
                    {selectedSample.patient_name} | Priority: <span className={selectedSample.priority === 'urgent' ? 'text-red-600 font-medium' : ''}>{selectedSample.priority}</span>
                  </p>
                </div>
                <button onClick={() => { setSelectedSample(null); setSelectedTest(null); }}
                  className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
              </div>

              {/* Test Selection */}
              {!selectedTest ? (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Select Test</h3>
                  <div className="space-y-2">
                    {(selectedSample.tests || []).map((t: any) => (
                      <button key={t.id || t.name}
                        onClick={() => selectTest(t)}
                        className="w-full text-left border rounded-lg p-3 hover:bg-gray-50 transition flex items-center justify-between">
                        <div>
                          <span className="font-medium text-gray-900">{t.name}</span>
                          <span className="text-xs text-gray-400 ml-2">{t.category}</span>
                        </div>
                        <span className="text-xs text-gray-400">{(t.parameters || []).length} parameters</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-gray-900">{selectedTest.name}</h3>
                      <p className="text-xs text-gray-400">{selectedTest.category} | {(selectedTest.parameters || []).length} parameters</p>
                    </div>
                    <button onClick={() => { setSelectedTest(null); setResults([]); }}
                      className="text-sm text-accent-600 hover:underline">Change Test</button>
                  </div>

                  {/* Parameter Entry */}
                  <div className="space-y-3 mb-4">
                    <div className="grid grid-cols-12 gap-2 text-xs font-medium text-gray-500 pb-1 border-b">
                      <div className="col-span-3">Parameter</div>
                      <div className="col-span-3">Value</div>
                      <div className="col-span-2">Unit</div>
                      <div className="col-span-3">Reference Range</div>
                      <div className="col-span-1">Status</div>
                    </div>
                    {results.map((r, i) => (
                      <div key={i} className={`grid grid-cols-12 gap-2 items-center rounded-lg p-2 ${
                        r.is_abnormal ? 'bg-red-50 border border-red-200' : ''
                      }`}>
                        <div className="col-span-3 text-sm font-medium text-gray-700">{r.name}</div>
                        <div className="col-span-3">
                          <input
                            className={`input-field text-sm ${r.is_abnormal ? 'border-red-300 text-red-700 font-semibold' : ''}`}
                            value={r.value}
                            onChange={(e) => updateResult(i, e.target.value)}
                            placeholder="Enter value"
                          />
                        </div>
                        <div className="col-span-2 text-sm text-gray-500">{r.unit}</div>
                        <div className="col-span-3 text-sm text-gray-400">{r.reference_range || '-'}</div>
                        <div className="col-span-1 text-center">
                          {r.value && (
                            r.is_abnormal
                              ? <AlertTriangle className="w-4 h-4 text-red-500 inline" />
                              : <CheckCircle className="w-4 h-4 text-green-500 inline" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Technician + Save */}
                  <div className="border-t pt-4 flex flex-col sm:flex-row gap-3 items-end">
                    <div className="flex-1">
                      <label className="block text-sm font-medium mb-1">Technician Name *</label>
                      <input className="input-field" value={technician}
                        onChange={(e) => setTechnician(e.target.value)} placeholder="Enter name" />
                    </div>
                    <button onClick={handleSave} disabled={saving}
                      className="btn-primary flex items-center gap-2 whitespace-nowrap px-6">
                      {saving ? (
                        <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                      ) : (
                        <Save className="w-4 h-4" />
                      )}
                      Save Results
                    </button>
                  </div>

                  {results.some((r) => r.is_abnormal) && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-sm text-red-700">
                      <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                      Some values are outside the reference range and will be highlighted in the report.
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="card py-16 text-center">
              <ClipboardList className="w-16 h-16 mx-auto mb-4 text-gray-200" />
              <h3 className="font-semibold text-gray-500 mb-1">Select a Sample</h3>
              <p className="text-sm text-gray-400">Choose a pending sample from the list to enter results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
