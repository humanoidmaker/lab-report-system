import { useState, useEffect } from 'react';
import api from '../utils/api';
import { TestTubes, FileText, CheckCircle, Users, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [reports, setReports] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, reportsRes] = await Promise.all([
        api.get('/reports/stats'),
        api.get('/reports?limit=10'),
      ]);
      setStats(statsRes.data);
      setReports(reportsRes.data.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const statCards = stats ? [
    { label: "Today's Samples", value: stats.today_samples, icon: TestTubes, color: 'bg-blue-500' },
    { label: 'Pending Results', value: stats.pending_results, icon: FileText, color: 'bg-orange-500' },
    { label: 'Verified Today', value: stats.verified_today, icon: CheckCircle, color: 'bg-green-500' },
    { label: 'Total Patients', value: stats.total_patients, icon: Users, color: 'bg-purple-500' },
  ] : [];

  const pipeline = stats?.pipeline || { collected: 0, processing: 0, completed: 0 };
  const pipelineTotal = pipeline.collected + pipeline.processing + pipeline.completed || 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <span className="text-sm text-gray-500">{new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s) => (
          <div key={s.label} className="card flex items-center gap-4">
            <div className={`${s.color} text-white p-3 rounded-lg`}>
              <s.icon className="w-6 h-6" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{s.value}</p>
              <p className="text-sm text-gray-500">{s.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Sample Pipeline */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Sample Pipeline</h2>
        <div className="flex gap-4 items-center">
          <div className="flex-1 text-center">
            <div className="text-3xl font-bold text-blue-600">{pipeline.collected}</div>
            <div className="text-sm text-gray-500 mt-1">Collected</div>
            <div className="mt-2 h-2 bg-blue-100 rounded-full">
              <div className="h-2 bg-blue-500 rounded-full" style={{ width: `${(pipeline.collected / pipelineTotal) * 100}%` }} />
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
          <div className="flex-1 text-center">
            <div className="text-3xl font-bold text-yellow-600">{pipeline.processing}</div>
            <div className="text-sm text-gray-500 mt-1">Processing</div>
            <div className="mt-2 h-2 bg-yellow-100 rounded-full">
              <div className="h-2 bg-yellow-500 rounded-full" style={{ width: `${(pipeline.processing / pipelineTotal) * 100}%` }} />
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
          <div className="flex-1 text-center">
            <div className="text-3xl font-bold text-green-600">{pipeline.completed}</div>
            <div className="text-sm text-gray-500 mt-1">Completed</div>
            <div className="mt-2 h-2 bg-green-100 rounded-full">
              <div className="h-2 bg-green-500 rounded-full" style={{ width: `${(pipeline.completed / pipelineTotal) * 100}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Reports</h2>
          <button onClick={() => navigate('/reports')} className="text-accent-600 text-sm hover:underline">View All</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-2 text-gray-500 font-medium">Report #</th>
                <th className="text-left py-3 px-2 text-gray-500 font-medium">Patient</th>
                <th className="text-left py-3 px-2 text-gray-500 font-medium">Test</th>
                <th className="text-left py-3 px-2 text-gray-500 font-medium">Status</th>
                <th className="text-left py-3 px-2 text-gray-500 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id} className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer" onClick={() => navigate('/reports')}>
                  <td className="py-3 px-2 font-medium text-primary-600">{r.report_number}</td>
                  <td className="py-3 px-2">{r.patient_name}</td>
                  <td className="py-3 px-2">{r.test_name}</td>
                  <td className="py-3 px-2">
                    <span className={r.status === 'verified' ? 'badge-verified' : 'badge-pending'}>
                      {r.status === 'verified' ? 'Verified' : 'Pending'}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-gray-500">{new Date(r.created_at).toLocaleDateString('en-IN')}</td>
                </tr>
              ))}
              {reports.length === 0 && (
                <tr><td colSpan={5} className="py-8 text-center text-gray-400">No reports yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
