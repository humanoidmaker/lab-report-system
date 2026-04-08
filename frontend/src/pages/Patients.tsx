import { useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import { Plus, Search, X, Users, Phone, User, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Patients() {
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showHistory, setShowHistory] = useState<any>(null);
  const [reports, setReports] = useState<any[]>([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: '', age: '', gender: 'Male', phone: '', email: '', address: '', doctor_name: '',
  });

  useEffect(() => { loadPatients(); }, []);

  const loadPatients = async () => {
    try {
      const { data } = await api.get('/patients');
      setPatients(data.data || []);
    } catch {
      toast.error('Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const searchPatients = async () => {
    if (!search.trim()) return loadPatients();
    setLoading(true);
    try {
      const { data } = await api.get('/patients/search', { params: { q: search } });
      setPatients(data.data || []);
    } catch {
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!form.name || !form.phone) return toast.error('Name and phone required');
    try {
      const payload = { ...form, age: parseInt(form.age) || 0 };
      if (editId) {
        await api.put(`/patients/${editId}`, payload);
        toast.success('Patient updated');
      } else {
        await api.post('/patients', payload);
        toast.success('Patient registered');
      }
      setShowForm(false);
      resetForm();
      loadPatients();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error saving patient');
    }
  };

  const openHistory = async (patient: any) => {
    setShowHistory(patient);
    setLoadingReports(true);
    try {
      const { data } = await api.get(`/reports?patient_id=${patient.id}`);
      setReports(data.data || []);
    } catch {
      setReports([]);
    } finally {
      setLoadingReports(false);
    }
  };

  const openEdit = (p: any) => {
    setEditId(p.id);
    setForm({
      name: p.name || '', age: String(p.age || ''), gender: p.gender || 'Male',
      phone: p.phone || '', email: p.email || '', address: p.address || '', doctor_name: p.doctor_name || '',
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setEditId(null);
    setForm({ name: '', age: '', gender: 'Male', phone: '', email: '', address: '', doctor_name: '' });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
        <button onClick={() => { resetForm(); setShowForm(true); }} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Patient
        </button>
      </div>

      {/* Search */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input
            className="input-field pl-9"
            placeholder="Search by name or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && searchPatients()}
          />
        </div>
        <button onClick={searchPatients} className="btn-primary px-5">Search</button>
      </div>

      {/* Patient Table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin h-8 w-8 border-4 border-accent-500 border-t-transparent rounded-full" />
        </div>
      ) : patients.length > 0 ? (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Name</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500 hidden sm:table-cell">Age</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500 hidden sm:table-cell">Gender</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Phone</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500 hidden md:table-cell">Doctor</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((p) => (
                <tr key={p.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-900">{p.name}</td>
                  <td className="py-3 px-4 text-gray-600 hidden sm:table-cell">{p.age || '-'}</td>
                  <td className="py-3 px-4 hidden sm:table-cell">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      p.gender === 'Male' ? 'bg-blue-100 text-blue-700'
                        : p.gender === 'Female' ? 'bg-pink-100 text-pink-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {p.gender}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-600">{p.phone}</td>
                  <td className="py-3 px-4 text-gray-600 hidden md:table-cell">{p.doctor_name || '-'}</td>
                  <td className="py-3 px-4 space-x-2">
                    <button onClick={() => openHistory(p)} className="text-accent-600 hover:underline text-xs font-medium">Reports</button>
                    <button onClick={() => openEdit(p)} className="text-primary-600 hover:underline text-xs font-medium">Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card py-12 text-center">
          <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-400 text-sm">No patients found</p>
          <button onClick={() => { resetForm(); setShowForm(true); }} className="mt-3 text-accent-600 text-sm hover:underline">
            Register first patient
          </button>
        </div>
      )}

      {/* Add/Edit Patient Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{editId ? 'Edit Patient' : 'Register Patient'}</h2>
              <button onClick={() => setShowForm(false)}><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Full Name *</label>
                <input className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Age</label>
                  <input className="input-field" type="number" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Gender</label>
                  <select className="input-field" value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })}>
                    <option>Male</option><option>Female</option><option>Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Phone *</label>
                  <input className="input-field" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input className="input-field" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Address</label>
                <input className="input-field" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Referring Doctor</label>
                <input className="input-field" value={form.doctor_name} onChange={(e) => setForm({ ...form, doctor_name: e.target.value })} />
              </div>
            </div>
            <div className="flex gap-3 justify-end mt-6">
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
              <button onClick={handleSave} className="btn-primary">{editId ? 'Update' : 'Register'} Patient</button>
            </div>
          </div>
        </div>
      )}

      {/* Report History Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold">{showHistory.name}</h2>
                <p className="text-sm text-gray-500">
                  {showHistory.age && `${showHistory.age}y`} {showHistory.gender} | {showHistory.phone}
                </p>
              </div>
              <button onClick={() => setShowHistory(null)}><X className="w-5 h-5" /></button>
            </div>

            <h3 className="font-semibold text-gray-900 mb-3">Report History</h3>
            {loadingReports ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin h-6 w-6 border-4 border-accent-500 border-t-transparent rounded-full" />
              </div>
            ) : reports.length > 0 ? (
              <div className="space-y-2">
                {reports.map((r) => (
                  <div key={r.id} className="flex items-center justify-between border rounded-lg p-3 hover:bg-gray-50">
                    <div>
                      <span className="font-medium text-primary-600 text-sm">{r.report_number}</span>
                      <span className="text-sm text-gray-600 ml-2">{r.test_name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={r.status === 'verified' ? 'badge-verified' : 'badge-pending'}>
                        {r.status === 'verified' ? 'Verified' : 'Pending'}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(r.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-gray-400 text-sm">
                <FileText className="w-10 h-10 mx-auto mb-2 opacity-40" />
                No reports for this patient
              </div>
            )}

            <div className="flex justify-end mt-4">
              <button onClick={() => setShowHistory(null)} className="btn-secondary">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
