import { useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import { Plus, Search, X, TestTubes } from 'lucide-react';

export default function Samples() {
  const [samples, setSamples] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQ, setSearchQ] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showDetail, setShowDetail] = useState<any>(null);

  // Form state
  const [patientSearch, setPatientSearch] = useState('');
  const [patientResults, setPatientResults] = useState<any[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [tests, setTests] = useState<any[]>([]);
  const [selectedTests, setSelectedTests] = useState<string[]>([]);
  const [priority, setPriority] = useState('routine');
  const [collectedBy, setCollectedBy] = useState('');

  // New patient form
  const [showNewPatient, setShowNewPatient] = useState(false);
  const [newPatient, setNewPatient] = useState({ name: '', age: '', gender: 'Male', phone: '', doctor_name: '' });

  useEffect(() => { loadSamples(); }, [statusFilter]);

  const loadSamples = async () => {
    try {
      const params: any = { limit: 200 };
      if (statusFilter) params.status = statusFilter;
      if (searchQ) params.q = searchQ;
      const { data } = await api.get('/samples', { params });
      setSamples(data.data || []);
    } catch (err) { console.error(err); }
  };

  const searchPatients = async (q: string) => {
    setPatientSearch(q);
    if (q.length >= 2) {
      const { data } = await api.get('/patients/search', { params: { q } });
      setPatientResults(data.data || []);
    } else {
      setPatientResults([]);
    }
  };

  const loadTests = async () => {
    const { data } = await api.get('/tests');
    setTests(data.data || []);
  };

  const openForm = () => {
    setShowForm(true);
    loadTests();
    setSelectedPatient(null);
    setSelectedTests([]);
    setPriority('routine');
    setCollectedBy('');
    setPatientSearch('');
  };

  const toggleTest = (id: string) => {
    setSelectedTests((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  const subtotal = tests.filter((t) => selectedTests.includes(t.id)).reduce((s, t) => s + t.price, 0);

  const handleSubmit = async () => {
    if (!selectedPatient) return toast.error('Select a patient');
    if (selectedTests.length === 0) return toast.error('Select at least one test');
    if (!collectedBy) return toast.error('Enter collected by name');
    try {
      await api.post('/samples', {
        patient_id: selectedPatient.id,
        test_ids: selectedTests,
        collected_by: collectedBy,
        priority,
      });
      toast.success('Sample registered!');
      setShowForm(false);
      loadSamples();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error creating sample');
    }
  };

  const handleNewPatient = async () => {
    if (!newPatient.name || !newPatient.phone) return toast.error('Name and phone required');
    try {
      const { data } = await api.post('/patients', {
        ...newPatient,
        age: parseInt(newPatient.age) || 0,
      });
      setSelectedPatient(data);
      setShowNewPatient(false);
      toast.success('Patient registered');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error');
    }
  };

  const updateStatus = async (id: string, status: string) => {
    try {
      await api.put(`/samples/${id}/status?status=${status}`);
      toast.success('Status updated');
      loadSamples();
      setShowDetail(null);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Samples</h1>
        <button onClick={openForm} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> Register Sample</button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input
            className="input-field pl-9"
            placeholder="Search by sample ID or patient..."
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadSamples()}
          />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field w-auto">
          <option value="">All Status</option>
          <option value="collected">Collected</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Sample list */}
      <div className="card p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Sample ID</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Patient</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Tests</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Priority</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            {samples.map((s) => (
              <tr key={s.id} className="border-t border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 font-medium text-primary-600">{s.sample_id}</td>
                <td className="py-3 px-4">{s.patient_name}</td>
                <td className="py-3 px-4">{(s.tests || []).map((t: any) => t.name).join(', ')}</td>
                <td className="py-3 px-4"><span className={s.priority === 'urgent' ? 'badge-urgent' : 'badge-routine'}>{s.priority}</span></td>
                <td className="py-3 px-4"><span className={`badge-${s.status}`}>{s.status}</span></td>
                <td className="py-3 px-4 text-gray-500">{new Date(s.created_at).toLocaleDateString('en-IN')}</td>
                <td className="py-3 px-4">
                  <button onClick={() => setShowDetail(s)} className="text-accent-600 hover:underline text-sm">View</button>
                </td>
              </tr>
            ))}
            {samples.length === 0 && (
              <tr><td colSpan={7} className="py-12 text-center text-gray-400">No samples found</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Register Sample Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Register New Sample</h2>
              <button onClick={() => setShowForm(false)}><X className="w-5 h-5" /></button>
            </div>

            {/* Patient selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Patient</label>
              {selectedPatient ? (
                <div className="flex items-center justify-between bg-primary-50 p-3 rounded-lg">
                  <div>
                    <span className="font-medium">{selectedPatient.name}</span>
                    <span className="text-gray-500 ml-2">{selectedPatient.phone}</span>
                  </div>
                  <button onClick={() => setSelectedPatient(null)} className="text-red-500 text-sm">Change</button>
                </div>
              ) : (
                <div>
                  <input
                    className="input-field"
                    placeholder="Search patient by name or phone..."
                    value={patientSearch}
                    onChange={(e) => searchPatients(e.target.value)}
                  />
                  {patientResults.length > 0 && (
                    <div className="border rounded-lg mt-1 max-h-40 overflow-y-auto">
                      {patientResults.map((p) => (
                        <div key={p.id} onClick={() => { setSelectedPatient(p); setPatientResults([]); }} className="px-3 py-2 hover:bg-gray-100 cursor-pointer">
                          {p.name} - {p.phone}
                        </div>
                      ))}
                    </div>
                  )}
                  <button onClick={() => setShowNewPatient(true)} className="text-accent-600 text-sm mt-2 hover:underline">+ Register New Patient</button>
                </div>
              )}
            </div>

            {/* New patient inline form */}
            {showNewPatient && (
              <div className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3">
                <h3 className="font-medium">New Patient</h3>
                <div className="grid grid-cols-2 gap-3">
                  <input className="input-field" placeholder="Name *" value={newPatient.name} onChange={(e) => setNewPatient({ ...newPatient, name: e.target.value })} />
                  <input className="input-field" placeholder="Phone *" value={newPatient.phone} onChange={(e) => setNewPatient({ ...newPatient, phone: e.target.value })} />
                  <input className="input-field" placeholder="Age" value={newPatient.age} onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })} />
                  <select className="input-field" value={newPatient.gender} onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value })}>
                    <option>Male</option><option>Female</option><option>Other</option>
                  </select>
                  <input className="input-field col-span-2" placeholder="Doctor Name" value={newPatient.doctor_name} onChange={(e) => setNewPatient({ ...newPatient, doctor_name: e.target.value })} />
                </div>
                <div className="flex gap-2">
                  <button onClick={handleNewPatient} className="btn-primary text-sm">Save Patient</button>
                  <button onClick={() => setShowNewPatient(false)} className="btn-secondary text-sm">Cancel</button>
                </div>
              </div>
            )}

            {/* Test selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Select Tests</label>
              <div className="border rounded-lg max-h-60 overflow-y-auto p-2 space-y-1">
                {tests.map((t) => (
                  <label key={t.id} className="flex items-center gap-3 px-3 py-2 hover:bg-gray-50 rounded cursor-pointer">
                    <input type="checkbox" checked={selectedTests.includes(t.id)} onChange={() => toggleTest(t.id)} className="rounded" />
                    <span className="flex-1">{t.name}</span>
                    <span className="text-xs text-gray-400">{t.category}</span>
                    <span className="text-sm font-medium">Rs. {t.price}</span>
                  </label>
                ))}
              </div>
              {selectedTests.length > 0 && (
                <div className="text-right mt-2 font-semibold text-primary-600">Subtotal: Rs. {subtotal}</div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <select className="input-field" value={priority} onChange={(e) => setPriority(e.target.value)}>
                  <option value="routine">Routine</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Collected By</label>
                <input className="input-field" value={collectedBy} onChange={(e) => setCollectedBy(e.target.value)} placeholder="Technician name" />
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
              <button onClick={handleSubmit} className="btn-primary">Register Sample</button>
            </div>
          </div>
        </div>
      )}

      {/* Sample Detail Modal */}
      {showDetail && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{showDetail.sample_id}</h2>
              <button onClick={() => setShowDetail(null)}><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between"><span className="text-gray-500">Patient:</span><span className="font-medium">{showDetail.patient_name}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Priority:</span><span className={showDetail.priority === 'urgent' ? 'badge-urgent' : 'badge-routine'}>{showDetail.priority}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Status:</span><span className={`badge-${showDetail.status}`}>{showDetail.status}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Collected By:</span><span>{showDetail.collected_by}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Total:</span><span className="font-semibold">Rs. {showDetail.total_price}</span></div>
              <div>
                <span className="text-gray-500 block mb-1">Tests:</span>
                <ul className="list-disc list-inside text-sm">
                  {(showDetail.tests || []).map((t: any, i: number) => (
                    <li key={i}>{t.name} (Rs. {t.price})</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="flex gap-3 justify-end mt-6">
              {showDetail.status === 'collected' && (
                <button onClick={() => updateStatus(showDetail.id, 'processing')} className="btn-accent">Start Processing</button>
              )}
              {showDetail.status === 'processing' && (
                <button onClick={() => updateStatus(showDetail.id, 'completed')} className="btn-primary">Mark Completed</button>
              )}
              <button onClick={() => setShowDetail(null)} className="btn-secondary">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
