import { useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import { Plus, X, Pencil, Trash2, ChevronDown, ChevronRight } from 'lucide-react';

interface Param {
  name: string;
  unit: string;
  reference_range_male: string;
  reference_range_female: string;
}

export default function Tests() {
  const [tests, setTests] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [expandedCat, setExpandedCat] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);

  const [form, setForm] = useState({
    name: '', category: 'Hematology', sample_type: 'blood', description: '', price: 0, turnaround_hours: 24,
  });
  const [params, setParams] = useState<Param[]>([]);

  const allCategories = ['Hematology', 'Biochemistry', 'Microbiology', 'Immunology', 'Urine', 'Thyroid', 'Lipid', 'Liver', 'Kidney', 'Other'];

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [testsRes, catRes] = await Promise.all([
        api.get('/tests'),
        api.get('/tests/categories'),
      ]);
      setTests(testsRes.data.data || []);
      setCategories(catRes.data.data || []);
    } catch (err) { console.error(err); }
  };

  const grouped = categories.reduce((acc: any, cat: string) => {
    acc[cat] = tests.filter((t) => t.category === cat);
    return acc;
  }, {});

  const openNew = () => {
    setEditId(null);
    setForm({ name: '', category: 'Hematology', sample_type: 'blood', description: '', price: 0, turnaround_hours: 24 });
    setParams([]);
    setShowForm(true);
  };

  const openEdit = (t: any) => {
    setEditId(t.id);
    setForm({ name: t.name, category: t.category, sample_type: t.sample_type, description: t.description || '', price: t.price, turnaround_hours: t.turnaround_hours });
    setParams(t.parameters || []);
    setShowForm(true);
  };

  const addParam = () => setParams([...params, { name: '', unit: '', reference_range_male: '', reference_range_female: '' }]);
  const removeParam = (i: number) => setParams(params.filter((_, idx) => idx !== i));
  const updateParam = (i: number, field: string, value: string) => {
    const copy = [...params];
    (copy[i] as any)[field] = value;
    setParams(copy);
  };

  const handleSave = async () => {
    if (!form.name) return toast.error('Test name required');
    try {
      const payload = { ...form, parameters: params };
      if (editId) {
        await api.put(`/tests/${editId}`, payload);
        toast.success('Test updated');
      } else {
        await api.post('/tests', payload);
        toast.success('Test created');
      }
      setShowForm(false);
      loadData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this test?')) return;
    try {
      await api.delete(`/tests/${id}`);
      toast.success('Test deleted');
      loadData();
    } catch (err) { toast.error('Error deleting'); }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Test Catalog</h1>
        <button onClick={openNew} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> Add Test</button>
      </div>

      {/* Grouped by category */}
      <div className="space-y-2">
        {categories.map((cat) => (
          <div key={cat} className="card p-0 overflow-hidden">
            <button
              onClick={() => setExpandedCat(expandedCat === cat ? '' : cat)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50"
            >
              <span className="font-semibold text-primary-600">{cat} ({grouped[cat]?.length || 0})</span>
              {expandedCat === cat ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
            </button>
            {expandedCat === cat && (
              <div className="border-t">
                {(grouped[cat] || []).map((t: any) => (
                  <div key={t.id} className="flex items-center justify-between px-4 py-3 border-b last:border-0 hover:bg-gray-50">
                    <div>
                      <span className="font-medium">{t.name}</span>
                      <span className="text-xs text-gray-400 ml-2">({t.sample_type})</span>
                      <span className="text-xs text-gray-400 ml-2">{t.parameters?.length || 0} params</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-gray-600">Rs. {t.price}</span>
                      <span className="text-xs text-gray-400">{t.turnaround_hours}h</span>
                      <button onClick={() => openEdit(t)} className="text-accent-600 hover:bg-accent-50 p-1 rounded"><Pencil className="w-4 h-4" /></button>
                      <button onClick={() => handleDelete(t.id)} className="text-red-500 hover:bg-red-50 p-1 rounded"><Trash2 className="w-4 h-4" /></button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{editId ? 'Edit Test' : 'New Test'}</h2>
              <button onClick={() => setShowForm(false)}><X className="w-5 h-5" /></button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1">Test Name</label>
                <input className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <select className="input-field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                  {allCategories.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Sample Type</label>
                <select className="input-field" value={form.sample_type} onChange={(e) => setForm({ ...form, sample_type: e.target.value })}>
                  <option value="blood">Blood</option>
                  <option value="urine">Urine</option>
                  <option value="stool">Stool</option>
                  <option value="swab">Swab</option>
                  <option value="sputum">Sputum</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Price (Rs.)</label>
                <input type="number" className="input-field" value={form.price} onChange={(e) => setForm({ ...form, price: Number(e.target.value) })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Turnaround (hours)</label>
                <input type="number" className="input-field" value={form.turnaround_hours} onChange={(e) => setForm({ ...form, turnaround_hours: Number(e.target.value) })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <input className="input-field" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
            </div>

            {/* Parameters builder */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="font-medium">Parameters</label>
                <button onClick={addParam} className="text-accent-600 text-sm hover:underline">+ Add Parameter</button>
              </div>
              <div className="space-y-2">
                {params.map((p, i) => (
                  <div key={i} className="grid grid-cols-5 gap-2 items-center bg-gray-50 p-2 rounded">
                    <input className="input-field text-sm" placeholder="Name" value={p.name} onChange={(e) => updateParam(i, 'name', e.target.value)} />
                    <input className="input-field text-sm" placeholder="Unit" value={p.unit} onChange={(e) => updateParam(i, 'unit', e.target.value)} />
                    <input className="input-field text-sm" placeholder="Ref Male" value={p.reference_range_male} onChange={(e) => updateParam(i, 'reference_range_male', e.target.value)} />
                    <input className="input-field text-sm" placeholder="Ref Female" value={p.reference_range_female} onChange={(e) => updateParam(i, 'reference_range_female', e.target.value)} />
                    <button onClick={() => removeParam(i)} className="text-red-500 hover:bg-red-50 p-1 rounded justify-self-center"><Trash2 className="w-4 h-4" /></button>
                  </div>
                ))}
                {params.length === 0 && <p className="text-sm text-gray-400">No parameters added</p>}
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
              <button onClick={handleSave} className="btn-primary">Save Test</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
